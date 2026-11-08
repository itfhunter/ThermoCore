"""Einrichtungsdialog: Hub, Pumpe, Raum mit Vorauswahl aus dem Bereich (erfundene Entitäten)."""

import pytest

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import area_registry as ar, entity_registry as er

DOMAIN = "thermocore"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


def _default(schema, key):
    for k in schema.schema:
        if k == key:
            d = k.default() if callable(k.default) else None
            return d if d is not None else (k.description or {}).get("suggested_value")
    return "<fehlt>"


async def test_full_setup_flow(hass: HomeAssistant):
    area = ar.async_get(hass).async_create("Example room")
    reg = er.async_get(hass)
    t = reg.async_get_or_create("sensor", "demo", "t1", suggested_object_id="example_temp", original_device_class="temperature")
    reg.async_update_entity(t.entity_id, area_id=area.id)
    v = reg.async_get_or_create("switch", "demo", "v1", suggested_object_id="example_valve")
    reg.async_update_entity(v.entity_id, area_id=area.id)

    # 1) Hub
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert r["type"] is FlowResultType.FORM
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {"target_temp": 21.0, "hysteresis": 0.2, "observe_only": True})
    assert r["type"] is FlowResultType.CREATE_ENTRY
    entry = r["result"]

    # 2) Pumpe
    r = await hass.config_entries.subentries.async_init((entry.entry_id, "pump"), context={"source": "user"})
    r = await hass.config_entries.subentries.async_configure(
        r["flow_id"], {"name": "Example pump", "pump_switch": "switch.example_pump", "lead_time": 120, "follow_time": 60})
    assert r["type"] is FlowResultType.CREATE_ENTRY
    pump_id = next(s for s, sub in entry.subentries.items() if sub.subentry_type == "pump")

    # 3) Raum: Bereich wählen -> Geräte vorgeschlagen, einzige Pumpe vorbelegt
    r = await hass.config_entries.subentries.async_init((entry.entry_id, "room"), context={"source": "user"})
    r = await hass.config_entries.subentries.async_configure(r["flow_id"], {"area_id": area.id, "room_type": "heating"})
    assert r["step_id"] == "devices"
    schema = r["data_schema"]
    assert _default(schema, "temp_sensor") == t.entity_id
    assert _default(schema, "heat_switch") == v.entity_id
    assert _default(schema, "pump_subentry_id") == pump_id
    assert r["description_placeholders"] == {"found_sensors": "1", "found_switches": "1"}
    r = await hass.config_entries.subentries.async_configure(
        r["flow_id"], {"temp_sensor": t.entity_id, "heat_switch": v.entity_id, "pump_subentry_id": pump_id})
    assert r["type"] is FlowResultType.CREATE_ENTRY
    room = next(sub for sub in entry.subentries.values() if sub.subentry_type == "room")
    assert room.title == "Example room"
    assert room.data["pump_subentry_id"] == pump_id


async def test_only_one_hub(hass: HomeAssistant):
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    await hass.config_entries.flow.async_configure(r["flow_id"], {"target_temp": 21.0, "hysteresis": 0.2, "observe_only": True})
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert r["type"] is FlowResultType.ABORT and r["reason"] == "already_configured"
