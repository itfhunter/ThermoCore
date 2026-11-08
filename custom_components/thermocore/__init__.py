"""ThermoCore – Raumweise Heizungssteuerung (Heizung = FBH/Heizkörper, später Klima)."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .controller import ThermoCoreController

PLATFORMS: list[str] = ["climate", "number", "switch", "select", "binary_sensor"]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

CARDS_URL = f"/{DOMAIN}/thermocore-cards.js"
CARDS_FILE = Path(__file__).parent / "frontend" / "thermocore-cards.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Dashboard-Karten einmalig bereitstellen (kein separater HACS-Download nötig)."""
    if hass.http is None or "frontend" not in hass.config.components:
        return True  # ohne Web-Oberfläche (z. B. Tests) keine Karten
    await hass.http.async_register_static_paths([StaticPathConfig(CARDS_URL, str(CARDS_FILE), True)])
    version = (await hass.async_add_executor_job(_manifest_version))
    add_extra_js_url(hass, f"{CARDS_URL}?v={version}")
    return True


def _manifest_version() -> str:
    import json

    return json.loads((Path(__file__).parent / "manifest.json").read_text())["version"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ctrl = ThermoCoreController(hass, entry)
    entry.runtime_data = ctrl
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await ctrl.async_start()
    entry.async_on_unload(entry.add_update_listener(_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await entry.runtime_data.async_stop()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
