"""Config-Flow für ThermoCore: Hub + Untereinträge Pumpe und Raum."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    selector as sel,
)

from .const import (
    CONF_AREA,
    CONF_HEAT_SWITCH,
    CONF_HYSTERESIS,
    CONF_LINKED_CLIMATE,
    CONF_OBSERVE_ONLY,
    CONF_OVERRIDE_HYST,
    CONF_OVERRIDE_TARGET,
    CONF_PUMP,
    CONF_PUMP_FOLLOW,
    CONF_PUMP_LEAD,
    CONF_PUMP_SWITCH,
    CONF_ROOM_TYPE,
    CONF_TARGET_TEMP,
    CONF_TEMP_SENSOR,
    DEFAULT_HYSTERESIS,
    DEFAULT_PUMP_FOLLOW,
    DEFAULT_PUMP_LEAD,
    DEFAULT_TARGET_TEMP,
    DOMAIN,
    ROOM_TYPE_FLOOR,
    ROOM_TYPES,
    SUBENTRY_PUMP,
    SUBENTRY_ROOM,
)

_TEMP = sel.NumberSelector(
    sel.NumberSelectorConfig(min=5, max=30, step=0.1, unit_of_measurement="°C", mode="box")
)
_HYST = sel.NumberSelector(
    sel.NumberSelectorConfig(min=0.1, max=2.0, step=0.1, unit_of_measurement="K", mode="box")
)
_SECONDS = sel.NumberSelector(
    sel.NumberSelectorConfig(min=0, max=1800, step=10, unit_of_measurement="s", mode="box")
)


def _hub_schema(d: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_TARGET_TEMP, default=d.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP)): _TEMP,
            vol.Required(CONF_HYSTERESIS, default=d.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS)): _HYST,
            vol.Required(CONF_OBSERVE_ONLY, default=d.get(CONF_OBSERVE_ONLY, True)): sel.BooleanSelector(),
        }
    )


def _area_entities(hass: HomeAssistant, area_id: str, domain: str, device_class: str | None = None) -> list[str]:
    """Entitäten eines Bereichs (direkt oder über das Gerät zugeordnet)."""
    ent_reg, dev_reg = er.async_get(hass), dr.async_get(hass)
    found: list[str] = []
    for ent in ent_reg.entities.values():
        if ent.domain != domain or ent.disabled_by:
            continue
        ent_area = ent.area_id
        if ent_area is None and ent.device_id and (dev := dev_reg.async_get(ent.device_id)):
            ent_area = dev.area_id
        if ent_area != area_id:
            continue
        if device_class and (ent.device_class or ent.original_device_class) != device_class:
            continue
        found.append(ent.entity_id)
    return sorted(found)


class ThermoCoreConfigFlow(ConfigFlow, domain=DOMAIN):
    """Haupteintrag: globale Einstellungen."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(title="ThermoCore", data={}, options=user_input)
        return self.async_show_form(step_id="user", data_schema=_hub_schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return ThermoCoreOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry: ConfigEntry) -> dict[str, type[ConfigSubentryFlow]]:
        return {SUBENTRY_PUMP: PumpSubentryFlow, SUBENTRY_ROOM: RoomSubentryFlow}


class ThermoCoreOptionsFlow(OptionsFlow):
    """Globale Einstellungen ändern."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(step_id="init", data_schema=_hub_schema(dict(self.config_entry.options)))


class PumpSubentryFlow(ConfigSubentryFlow):
    """Umwälzpumpe anlegen/ändern."""

    def _schema(self, d: dict[str, Any]) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name", default=d.get("name", "")): sel.TextSelector(),
                vol.Required(CONF_PUMP_SWITCH, default=d.get(CONF_PUMP_SWITCH)): sel.EntitySelector(
                    sel.EntitySelectorConfig(domain="switch")
                ),
                vol.Required(CONF_PUMP_LEAD, default=d.get(CONF_PUMP_LEAD, DEFAULT_PUMP_LEAD)): _SECONDS,
                vol.Required(CONF_PUMP_FOLLOW, default=d.get(CONF_PUMP_FOLLOW, DEFAULT_PUMP_FOLLOW)): _SECONDS,
            }
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        if user_input is not None:
            return self.async_create_entry(title=user_input["name"], data=user_input)
        return self.async_show_form(step_id="user", data_schema=self._schema({}))

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        sub = self._get_reconfigure_subentry()
        if user_input is not None:
            return self.async_update_and_abort(self._get_entry(), sub, title=user_input["name"], data=user_input)
        return self.async_show_form(step_id="reconfigure", data_schema=self._schema(dict(sub.data)))


class RoomSubentryFlow(ConfigSubentryFlow):
    """Raum anlegen: Schritt 1 Bereich + Typ, Schritt 2 Geräte (vorgeschlagen aus dem Bereich)."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_devices()
        schema = vol.Schema(
            {
                vol.Required(CONF_AREA): sel.AreaSelector(),
                vol.Required(CONF_ROOM_TYPE, default=ROOM_TYPE_FLOOR): sel.SelectSelector(
                    sel.SelectSelectorConfig(options=ROOM_TYPES, translation_key="room_type", mode="list")
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        self._data = dict(self._get_reconfigure_subentry().data)
        return await self.async_step_devices()

    async def async_step_devices(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        entry = self._get_entry()
        if user_input is not None:
            self._data.update(user_input)
            area = ar.async_get(self.hass).async_get_area(self._data[CONF_AREA])
            title = area.name if area else self._data[CONF_AREA]
            if self.source == "reconfigure":
                return self.async_update_and_abort(
                    entry, self._get_reconfigure_subentry(), title=title, data=self._data
                )
            return self.async_create_entry(title=title, data=self._data)

        area_id = self._data[CONF_AREA]
        sensors = _area_entities(self.hass, area_id, "sensor", "temperature")
        switches = _area_entities(self.hass, area_id, "switch")
        pumps = [
            sel.SelectOptionDict(value=sid, label=s.title)
            for sid, s in entry.subentries.items()
            if s.subentry_type == SUBENTRY_PUMP
        ]
        d = self._data
        fields: dict[Any, Any] = {
            vol.Required(CONF_TEMP_SENSOR, default=d.get(CONF_TEMP_SENSOR, sensors[0] if sensors else vol.UNDEFINED)): sel.EntitySelector(
                sel.EntitySelectorConfig(domain="sensor", device_class="temperature")
            ),
            vol.Required(CONF_HEAT_SWITCH, default=d.get(CONF_HEAT_SWITCH, switches[0] if switches else vol.UNDEFINED)): sel.EntitySelector(
                sel.EntitySelectorConfig(domain="switch")
            ),
        }
        if pumps:
            fields[vol.Optional(CONF_PUMP, description={"suggested_value": d.get(CONF_PUMP)})] = sel.SelectSelector(
                sel.SelectSelectorConfig(options=pumps, mode="dropdown")
            )
        fields[vol.Optional(CONF_OVERRIDE_TARGET, description={"suggested_value": d.get(CONF_OVERRIDE_TARGET)})] = _TEMP
        fields[vol.Optional(CONF_OVERRIDE_HYST, description={"suggested_value": d.get(CONF_OVERRIDE_HYST)})] = _HYST
        fields[vol.Optional(CONF_LINKED_CLIMATE, description={"suggested_value": d.get(CONF_LINKED_CLIMATE)})] = sel.EntitySelector(
            sel.EntitySelectorConfig(domain="climate")
        )
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(fields),
            description_placeholders={"found_sensors": str(len(sensors)), "found_switches": str(len(switches))},
        )
