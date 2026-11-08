"""Gemeinsame Basis für ThermoCore-Entitäten."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, signal_update
from .controller import ThermoCoreController


class ThermoCoreEntity(Entity):
    """Hängt an Hub-, Raum- oder Pumpen-Gerät und aktualisiert sich bei jedem Controller-Durchlauf."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, ctrl: ThermoCoreController, key: str, sid: str | None = None, name: str | None = None) -> None:
        self.ctrl = ctrl
        self.sid = sid
        entry_id = ctrl.entry.entry_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry_id}_{sid or 'hub'}_{key}"
        if sid is None:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, entry_id)}, name="ThermoCore", manufacturer="ThermoCore", model="Hub"
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{entry_id}_{sid}")}, name=name, manufacturer="ThermoCore",
                model="Pump" if sid in ctrl.pumps else "Room",
            )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal_update(self.ctrl.entry.entry_id), self.async_write_ha_state)
        )
