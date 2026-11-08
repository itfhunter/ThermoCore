"""Pumpenstatus (läuft / Standby), optional mit Leistung."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entity import ThermoCoreEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    ctrl = entry.runtime_data
    for sid, pump in ctrl.pumps.items():
        async_add_entities([PumpRunning(ctrl, sid, pump.name)], config_subentry_id=sid)


class PumpRunning(ThermoCoreEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, ctrl, sid: str, name: str) -> None:
        super().__init__(ctrl, "pump_running", sid, name)

    @property
    def _pump(self):
        return self.ctrl.pumps[self.sid]

    @property
    def available(self) -> bool:
        st = self.hass.states.get(self._pump.switch)
        return st is not None and st.state not in ("unavailable", "unknown")

    @property
    def is_on(self) -> bool:
        return self.ctrl._is_on(self._pump.switch)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        p = self._pump
        return {"power": self.ctrl.pump_power(p), "heat_demand": p.demand, "target_on": p.want_on,
                "lead_time": p.lead, "follow_time": p.follow}
