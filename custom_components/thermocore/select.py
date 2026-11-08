"""Betriebsart: Winter / Sommer / Manuell."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import OPERATING_MODES
from .entity import ThermoCoreEntity


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    async_add_entities([ModeSelect(entry.runtime_data)])


class ModeSelect(ThermoCoreEntity, SelectEntity):
    _attr_options = OPERATING_MODES

    def __init__(self, ctrl) -> None:
        super().__init__(ctrl, "operating_mode")

    @property
    def current_option(self) -> str:
        return self.ctrl.mode

    async def async_select_option(self, option: str) -> None:
        self.ctrl.set_global(mode=option)
