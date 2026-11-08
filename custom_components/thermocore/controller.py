"""Controller: verbindet Regelkern (logic.py) mit Home Assistant.

- Hält globale Werte und Raum-Einstellungen (persistiert über Store).
- Wertet bei jeder Änderung von Temperatur, Relais oder Einstellungen neu aus.
- Schaltet Raum-Relais und Pumpen nur über deren HA-Entitäten.
- Failsafe: alle CHECK_INTERVAL Sekunden werden Soll-Zustände erneut durchgesetzt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import time
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from datetime import timedelta

from . import logic
from .const import (
    API_VERSION,
    CHECK_INTERVAL,
    CONF_HEAT_SWITCH,
    CONF_HYSTERESIS,
    CONF_OBSERVE_ONLY,
    CONF_OVERRIDE_HYST,
    CONF_OVERRIDE_TARGET,
    CONF_PUMP,
    CONF_PUMP_FOLLOW,
    CONF_PUMP_LEAD,
    CONF_PUMP_POWER,
    CONF_PUMP_SWITCH,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    DEFAULT_HYSTERESIS,
    DEFAULT_PUMP_FOLLOW,
    DEFAULT_PUMP_LEAD,
    DEFAULT_TARGET_TEMP,
    DOMAIN,
    EVENT_ROOM_DEMAND,
    MODE_MANUAL,
    MODE_WINTER,
    STORAGE_VERSION,
    SUBENTRY_PUMP,
    SUBENTRY_ROOM,
    UNAVAILABLE_GRACE,
    signal_update,
)

_LOGGER = logging.getLogger(__name__)
_BAD = (STATE_UNAVAILABLE, STATE_UNKNOWN, None)


@dataclass
class Room:
    sid: str
    name: str
    sensor: str
    valve: str
    pump: str | None
    enabled: bool = True
    ov_target_on: bool = False
    ov_target: float = DEFAULT_TARGET_TEMP
    ov_hyst_on: bool = False
    ov_hyst: float = DEFAULT_HYSTERESIS
    # Laufzeit
    current: float | None = None
    demand: bool = False
    want_valve: bool = False
    bad_since: float | None = None


@dataclass
class Pump:
    sid: str
    name: str
    switch: str
    lead: float
    follow: float
    power_sensor: str | None
    state: logic.PumpState = field(default_factory=logic.PumpState)
    demand: bool = False
    want_on: bool = False


class ThermoCoreController:
    """Eine Instanz pro ThermoCore-Eintrag."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.api_version = API_VERSION
        opts = entry.options
        self.base_target: float = float(opts.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP))
        self.hysteresis: float = float(opts.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))
        self.observe_only: bool = bool(opts.get(CONF_OBSERVE_ONLY, True))
        self.heating: bool = True
        self.mode: str = MODE_WINTER
        self.rooms: dict[str, Room] = {}
        self.pumps: dict[str, Pump] = {}
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self._unsubs: list[CALLBACK_TYPE] = []
        self._pump_timer: CALLBACK_TYPE | None = None

        for sid, sub in entry.subentries.items():
            d = sub.data
            if sub.subentry_type == SUBENTRY_PUMP:
                self.pumps[sid] = Pump(
                    sid, sub.title, d[CONF_PUMP_SWITCH],
                    float(d.get(CONF_PUMP_LEAD, DEFAULT_PUMP_LEAD)), float(d.get(CONF_PUMP_FOLLOW, DEFAULT_PUMP_FOLLOW)),
                    d.get(CONF_PUMP_POWER),
                )
            elif sub.subentry_type == SUBENTRY_ROOM:
                self.rooms[sid] = Room(
                    sid, sub.title, d[CONF_TEMP_SENSOR], d[CONF_HEAT_SWITCH], d.get(CONF_PUMP),
                    ov_target_on=d.get(CONF_OVERRIDE_TARGET) is not None,
                    ov_target=float(d.get(CONF_OVERRIDE_TARGET) or self.base_target),
                    ov_hyst_on=d.get(CONF_OVERRIDE_HYST) is not None,
                    ov_hyst=float(d.get(CONF_OVERRIDE_HYST) or self.hysteresis),
                )

    # ---------- Lebenszyklus ----------
    async def async_start(self) -> None:
        await self._load()
        for p in self.pumps.values():  # nach Neustart vom tatsächlichen Zustand ausgehen
            p.state.on = self._is_on(p.switch)
        watch = [r.sensor for r in self.rooms.values()] + [r.valve for r in self.rooms.values()]
        watch += [p.switch for p in self.pumps.values()] + [p.power_sensor for p in self.pumps.values() if p.power_sensor]
        if watch:
            self._unsubs.append(async_track_state_change_event(self.hass, watch, self._on_state))
        self._unsubs.append(
            async_track_time_interval(self.hass, self._on_interval, timedelta(seconds=CHECK_INTERVAL))
        )
        self.evaluate()

    async def async_stop(self) -> None:
        for u in self._unsubs:
            u()
        self._unsubs.clear()
        if self._pump_timer:
            self._pump_timer()
            self._pump_timer = None

    # ---------- Persistenz ----------
    async def _load(self) -> None:
        data = await self._store.async_load() or {}
        g = data.get("global", {})
        # Wurden die globalen Werte im Konfigurationsdialog geändert, gelten diese; sonst der zuletzt gesetzte Wert.
        if data.get("options") == dict(self.entry.options):
            self.base_target = float(g.get("base_target", self.base_target))
            self.hysteresis = float(g.get("hysteresis", self.hysteresis))
        self.heating = bool(g.get("heating", self.heating))
        self.mode = g.get("mode", self.mode)
        for sid, rd in data.get("rooms", {}).items():
            if r := self.rooms.get(sid):
                r.enabled = rd.get("enabled", r.enabled)
                r.ov_target_on = rd.get("ov_target_on", r.ov_target_on)
                r.ov_target = float(rd.get("ov_target", r.ov_target))
                r.ov_hyst_on = rd.get("ov_hyst_on", r.ov_hyst_on)
                r.ov_hyst = float(rd.get("ov_hyst", r.ov_hyst))

    def _save(self) -> None:
        self._store.async_delay_save(self._dump, 2)

    def _dump(self) -> dict[str, Any]:
        return {
            "options": dict(self.entry.options),
            "global": {"base_target": self.base_target, "hysteresis": self.hysteresis, "heating": self.heating, "mode": self.mode},
            "rooms": {
                sid: {"enabled": r.enabled, "ov_target_on": r.ov_target_on, "ov_target": r.ov_target,
                      "ov_hyst_on": r.ov_hyst_on, "ov_hyst": r.ov_hyst}
                for sid, r in self.rooms.items()
            },
        }

    # ---------- Setter für Entitäten ----------
    def set_global(self, **kw: Any) -> None:
        for k, v in kw.items():
            setattr(self, k, v)
        self._save()
        self.evaluate()

    def set_room(self, sid: str, **kw: Any) -> None:
        r = self.rooms[sid]
        for k, v in kw.items():
            setattr(r, k, v)
        self._save()
        self.evaluate()

    # ---------- Abfragen ----------
    def room_target(self, r: Room) -> float:
        return logic.effective(self.base_target, r.ov_target_on, r.ov_target)

    def room_hyst(self, r: Room) -> float:
        return logic.effective(self.hysteresis, r.ov_hyst_on, r.ov_hyst)

    @property
    def regulating(self) -> bool:
        """Regelt ThermoCore gerade aktiv? (Winter + Heizung an)"""
        return self.heating and self.mode == MODE_WINTER

    def pump_power(self, p: Pump) -> float | None:
        st = self.hass.states.get(p.power_sensor) if p.power_sensor else None
        try:
            return float(st.state) if st else None
        except ValueError:
            return None

    # ---------- Auswertung ----------
    @callback
    def _on_state(self, event: Event) -> None:
        self.evaluate()

    @callback
    def _on_interval(self, _now: Any) -> None:
        self.evaluate(enforce=True)

    @callback
    def evaluate(self, enforce: bool = False) -> None:
        """Alles neu berechnen und (außer im Beobachtungs-/Handbetrieb) schalten."""
        now = time.monotonic()
        for r in self.rooms.values():
            r.current = self._temp(r.sensor)
            self._track_unavailable(r, now)
            prev = r.demand
            active = self.regulating and r.enabled
            r.demand = logic.room_demand(r.current, self.room_target(r), self.room_hyst(r), prev) if active else False
            r.want_valve = r.demand
            if r.demand != prev:
                self.hass.bus.async_fire(EVENT_ROOM_DEMAND, {
                    "entry_id": self.entry.entry_id, "room_id": r.sid, "name": r.name, "demand": r.demand,
                    "target": self.room_target(r), "current": r.current, "api_version": API_VERSION,
                })

        if self._pump_timer:
            self._pump_timer()
            self._pump_timer = None
        wake: float | None = None
        for p in self.pumps.values():
            p.demand = any(r.demand for r in self.rooms.values() if r.pump == p.sid)
            if not self.regulating:  # Sommer/aus: Pumpe sofort aus, Timer zurücksetzen
                p.state = logic.PumpState()
                p.want_on = False
                continue
            p.want_on = logic.pump_step(p.state, now, p.demand, p.lead, p.follow)
            w = logic.pump_next_wakeup(p.state, now, p.lead, p.follow)
            if w is not None:
                wake = w if wake is None else min(wake, w)
        if wake is not None:
            self._pump_timer = async_call_later(self.hass, wake + 0.1, self._on_pump_timer)

        if not self.observe_only and self.mode != MODE_MANUAL:
            for r in self.rooms.values():
                self._apply(r.valve, r.want_valve)
            for p in self.pumps.values():
                self._apply(p.switch, p.want_on)

        async_dispatcher_send(self.hass, signal_update(self.entry.entry_id))

    @callback
    def _on_pump_timer(self, _now: Any) -> None:
        self._pump_timer = None
        self.evaluate()

    # ---------- Hilfen ----------
    def _temp(self, entity_id: str) -> float | None:
        st = self.hass.states.get(entity_id)
        if st is None or st.state in _BAD:
            return None
        try:
            return float(st.state)
        except ValueError:
            return None

    def _is_on(self, entity_id: str) -> bool:
        st = self.hass.states.get(entity_id)
        return st is not None and st.state == STATE_ON

    def _apply(self, entity_id: str, on: bool) -> None:
        st = self.hass.states.get(entity_id)
        if st is None or st.state in _BAD or (st.state == STATE_ON) == on:
            return
        domain = entity_id.split(".", 1)[0]
        self.hass.async_create_task(
            self.hass.services.async_call(domain, "turn_on" if on else "turn_off", {"entity_id": entity_id}, blocking=False)
        )

    def _track_unavailable(self, r: Room, now: float) -> None:
        bad = r.current is None or self.hass.states.get(r.valve) is None or self.hass.states.get(r.valve).state in _BAD
        issue_id = f"unavailable_{self.entry.entry_id}_{r.sid}"
        if not bad:
            if r.bad_since is not None:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)
            r.bad_since = None
            return
        if r.bad_since is None:
            r.bad_since = now
        elif now - r.bad_since >= UNAVAILABLE_GRACE:
            ir.async_create_issue(
                self.hass, DOMAIN, issue_id, is_fixable=False, severity=ir.IssueSeverity.WARNING,
                translation_key="room_unavailable", translation_placeholders={"room": r.name},
            )
