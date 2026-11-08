"""Raum-Thermostat (eine climate-Entität pro Raum)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import ThermoCoreEntity

# Ab HA 2026.11 heißen die Temperatur-Eigenschaften native_*; ältere Versionen kennen nur die alten Namen.
_NATIVE = hasattr(ClimateEntity, "native_current_temperature")


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    ctrl = entry.runtime_data
    for sid, room in ctrl.rooms.items():
        async_add_entities([RoomClimate(ctrl, sid, room.name)], config_subentry_id=sid)


class RoomClimate(ThermoCoreEntity, ClimateEntity):
    _attr_name = None  # Gerätename = Raumname
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_target_temperature_step = 0.1
    _attr_min_temp = 5
    _attr_max_temp = 30
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, ctrl, sid: str, name: str) -> None:
        super().__init__(ctrl, "room", sid, name)
        if _NATIVE:
            self._attr_native_temperature_unit = UnitOfTemperature.CELSIUS
        else:
            self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def _room(self):
        return self.ctrl.rooms[self.sid]

    def _current(self) -> float | None:
        return self._room.current

    def _target(self) -> float:
        return self.ctrl.room_target(self._room)

    if _NATIVE:
        native_current_temperature = property(_current)
        native_target_temperature = property(_target)
    else:
        current_temperature = property(_current)
        target_temperature = property(_target)

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.HEAT if self._room.enabled else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        r = self._room
        if not r.enabled or not self.ctrl.regulating:
            return HVACAction.OFF
        return HVACAction.HEATING if r.demand else HVACAction.IDLE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        r = self._room
        return {
            "heat_demand": r.demand,
            "hysteresis": self.ctrl.room_hyst(r),
            "target_overridden": r.ov_target_on,
            "hysteresis_overridden": r.ov_hyst_on,
            "pump": self.ctrl.pumps[r.pump].name if r.pump in self.ctrl.pumps else None,
            "observe_only": self.ctrl.observe_only,
            "api_version": self.ctrl.api_version,
        }

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        self.ctrl.set_room(self.sid, enabled=hvac_mode == HVACMode.HEAT)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Soll am Thermostat setzen = Raum-Override einschalten."""
        if (t := kwargs.get(ATTR_TEMPERATURE)) is not None:
            self.ctrl.set_room(self.sid, ov_target_on=True, ov_target=float(t))
