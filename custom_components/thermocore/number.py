"""Zahlenwerte: globaler Sollwert/Hysterese und Raum-Overrides."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import ThermoCoreEntity

# key: (min, max, step, Controller-Attribut global | Raum-Attribut)
_GLOBAL = {"base_target": (15, 28, 0.1, "base_target"), "hysteresis": (0.1, 2.0, 0.1, "hysteresis")}
_ROOM = {"target_override": (5, 30, 0.1, "ov_target"), "hysteresis_override": (0.1, 2.0, 0.1, "ov_hyst")}


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    ctrl = entry.runtime_data
    async_add_entities([TCNumber(ctrl, k, *v) for k, v in _GLOBAL.items()])
    for sid, room in ctrl.rooms.items():
        async_add_entities([TCNumber(ctrl, k, *v, sid=sid, name=room.name) for k, v in _ROOM.items()], config_subentry_id=sid)


class TCNumber(ThermoCoreEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, ctrl, key, vmin, vmax, step, attr, sid=None, name=None) -> None:
        super().__init__(ctrl, key, sid, name)
        self._attr_native_min_value, self._attr_native_max_value, self._attr_native_step = vmin, vmax, step
        self._attr = attr

    @property
    def native_value(self) -> float:
        src = self.ctrl.rooms[self.sid] if self.sid else self.ctrl
        return round(float(getattr(src, self._attr)), 2)

    async def async_set_native_value(self, value: float) -> None:
        value = round(float(value), 2)
        if self.sid:
            self.ctrl.set_room(self.sid, **{self._attr: value})
        else:
            self.ctrl.set_global(**{self._attr: value})
