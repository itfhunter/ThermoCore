"""Integrationstests in echter Home-Assistant-Testumgebung – nur erfundene Entitäten."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from homeassistant.config_entries import ConfigSubentryData
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

DOMAIN = "thermocore"
TEMP = "sensor.example_room_temperature"
# Relais als input_boolean simuliert: die echte switch-Domäne lädt ThermoCore selbst (eigene Schalter).
VALVE = "input_boolean.example_room_valve"
PUMP = "input_boolean.example_pump"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
async def calls(hass: HomeAssistant):
    return {"on": async_mock_service(hass, "input_boolean", "turn_on"), "off": async_mock_service(hass, "input_boolean", "turn_off")}


def _switched(calls, kind):
    return [c.data["entity_id"] for c in calls[kind]]


async def _setup(hass, temp="20.0", valve="off", pump="off", observe=False, lead=0, follow=0, with_pump=True):
    hass.states.async_set(TEMP, temp, {"device_class": "temperature", "unit_of_measurement": "°C"})
    hass.states.async_set(VALVE, valve)
    hass.states.async_set(PUMP, pump)
    subs = [ConfigSubentryData(data={"area_id": "example", "room_type": "heating", "temp_sensor": TEMP,
                                     "heat_switch": VALVE, **({"pump_subentry_id": "p1"} if with_pump else {})},
                               subentry_id="r1", subentry_type="room", title="Example room", unique_id=None)]
    if with_pump:
        subs.append(ConfigSubentryData(data={"name": "Example pump", "pump_switch": PUMP, "lead_time": lead, "follow_time": follow},
                                       subentry_id="p1", subentry_type="pump", title="Example pump", unique_id=None))
    entry = MockConfigEntry(domain=DOMAIN, unique_id=DOMAIN, title="ThermoCore",
                            options={"target_temp": 21.0, "hysteresis": 0.2, "observe_only": observe}, subentries_data=subs)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _eid(hass, key, sid="hub"):
    reg = er.async_get(hass)
    for e in reg.entities.values():
        if e.platform == DOMAIN and e.translation_key == key and e.unique_id.endswith(f"_{sid}_{key}"):
            return e.entity_id
    raise AssertionError(f"Entität {key} fehlt")


async def test_entities_created_for_cards(hass, calls):
    """Alle Entitäten, die die Karten erwarten, existieren mit translation_key."""
    await _setup(hass)
    for key in ("base_target", "hysteresis", "heating", "operating_mode"):
        assert hass.states.get(_eid(hass, key)) is not None
    for key in ("room", "override_target", "target_override", "override_hysteresis", "hysteresis_override"):
        assert hass.states.get(_eid(hass, key, "r1")) is not None
    assert hass.states.get(_eid(hass, "pump_running", "p1")) is not None
    climate = hass.states.get(_eid(hass, "room", "r1"))
    assert climate.attributes["current_temperature"] == 20.0
    assert climate.attributes["temperature"] == 21.0


async def test_cold_room_opens_valve_and_starts_pump(hass, calls):
    await _setup(hass, temp="20.0")
    assert VALVE in _switched(calls, "on")
    assert PUMP in _switched(calls, "on")
    assert hass.states.get(_eid(hass, "room", "r1")).attributes["hvac_action"] == "heating"


async def test_warm_room_closes_valve_and_stops_pump(hass, calls):
    await _setup(hass, temp="21.5", valve="on", pump="on")
    assert VALVE in _switched(calls, "off")
    assert PUMP in _switched(calls, "off")


async def test_hysteresis_band_keeps_state(hass, calls):
    """20,9 °C liegt im Band (20,8–21,0): ein geschlossenes Ventil bleibt zu."""
    await _setup(hass, temp="20.9")
    assert VALVE not in _switched(calls, "on")


async def test_reacts_to_temperature_change(hass, calls):
    await _setup(hass, temp="21.5")
    hass.states.async_set(TEMP, "20.5", {"device_class": "temperature"})
    await hass.async_block_till_done()
    assert VALVE in _switched(calls, "on")


async def test_room_override_and_global_target(hass, calls):
    await _setup(hass, temp="21.5")
    # Globales Soll auf 23 -> Raum ist zu kalt
    await hass.services.async_call("number", "set_value", {"entity_id": _eid(hass, "base_target"), "value": 23}, blocking=True)
    assert VALVE in _switched(calls, "on")
    # Raum-Override 20 aktivieren -> Raum ist warm genug (Ventil-Zustand im Test bleibt 'off', also kein neuer Befehl)
    await hass.services.async_call("number", "set_value", {"entity_id": _eid(hass, "target_override", "r1"), "value": 20}, blocking=True)
    await hass.services.async_call("switch", "turn_on", {"entity_id": _eid(hass, "override_target", "r1")}, blocking=True)
    climate = hass.states.get(_eid(hass, "room", "r1"))
    assert climate.attributes["temperature"] == 20
    assert climate.attributes["heat_demand"] is False


async def test_observe_mode_never_switches(hass, calls):
    await _setup(hass, temp="19.0", observe=True)
    assert _switched(calls, "on") == [] and _switched(calls, "off") == []
    assert hass.states.get(_eid(hass, "room", "r1")).attributes["heat_demand"] is True


async def test_summer_and_manual_modes(hass, calls):
    await _setup(hass, temp="19.0", valve="on", pump="on")
    mode = _eid(hass, "operating_mode")
    calls["off"].clear()
    await hass.services.async_call("select", "select_option", {"entity_id": mode, "option": "summer"}, blocking=True)
    assert VALVE in _switched(calls, "off") and PUMP in _switched(calls, "off")
    # Manuell: ThermoCore schaltet gar nichts
    await hass.services.async_call("select", "select_option", {"entity_id": mode, "option": "manual"}, blocking=True)
    calls["on"].clear(); calls["off"].clear()
    hass.states.async_set(TEMP, "15.0")
    await hass.async_block_till_done()
    assert VALVE not in _switched(calls, "on") + _switched(calls, "off")


async def test_room_stop_closes_valve(hass, calls):
    await _setup(hass, temp="19.0", valve="on")
    await hass.services.async_call("climate", "set_hvac_mode", {"entity_id": _eid(hass, "room", "r1"), "hvac_mode": "off"}, blocking=True)
    assert VALVE in _switched(calls, "off")
    assert hass.states.get(_eid(hass, "room", "r1")).state == "off"


async def test_sensor_unavailable_is_safe(hass, calls):
    await _setup(hass, temp="19.0", valve="on")
    calls["off"].clear()
    hass.states.async_set(TEMP, "unavailable")
    await hass.async_block_till_done()
    assert VALVE in _switched(calls, "off")


async def test_pump_lead_time_delays_start(hass, calls):
    await _setup(hass, temp="19.0", lead=180)
    assert VALVE in _switched(calls, "on")
    assert PUMP not in _switched(calls, "on")  # Ventile zuerst, Pumpe erst nach Vorlauf


async def test_room_without_pump(hass, calls):
    await _setup(hass, temp="19.0", with_pump=False)
    assert VALVE in _switched(calls, "on")


async def test_values_survive_restart(hass, calls):
    entry = await _setup(hass, temp="21.5")
    await hass.services.async_call("number", "set_value", {"entity_id": _eid(hass, "base_target"), "value": 22.5}, blocking=True)
    await hass.async_block_till_done()
    ctrl = entry.runtime_data
    await ctrl._store.async_save(ctrl._dump())
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert float(hass.states.get(_eid(hass, "base_target")).state) == 22.5


async def test_demand_event_fired(hass, calls):
    events = []
    hass.bus.async_listen("thermocore_room_demand", lambda e: events.append(e.data))
    await _setup(hass, temp="19.0")
    await hass.async_block_till_done()
    assert events and events[-1]["demand"] is True and events[-1]["api_version"] == 1
