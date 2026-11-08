"""Schalter: globale Heizungsfreigabe und Raum-Override an/aus."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import ThermoCoreEntity

_ROOM = {"override_target": "ov_target_on", "override_hysteresis": "ov_hyst_on", "manual_heat": "manual_on"}


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    ctrl = entry.runtime_data
    async_add_entities([TCSwitch(ctrl, "heating", "heating")])
    for sid, room in ctrl.rooms.items():
        async_add_entities([TCSwitch(ctrl, k, a, sid, room.name) for k, a in _ROOM.items()], config_subentry_id=sid)


class TCSwitch(ThermoCoreEntity, SwitchEntity):
    def __init__(self, ctrl, key: str, attr: str, sid=None, name=None) -> None:
        super().__init__(ctrl, key, sid, name)
        self._attr = attr

    @property
    def available(self) -> bool:
        """'Manuell heizen' ist nur im Handbetrieb bedienbar."""
        return self._attr != "manual_on" or self.ctrl.manual

    @property
    def is_on(self) -> bool:
        return bool(getattr(self.ctrl.rooms[self.sid] if self.sid else self.ctrl, self._attr))

    async def _set(self, on: bool) -> None:
        if self.sid:
            self.ctrl.set_room(self.sid, **{self._attr: on})
        else:
            self.ctrl.set_global(**{self._attr: on})

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set(False)
