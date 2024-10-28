"""Tuya Vacuum Maps integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up the Tuya Vacuum Maps integration."""
    hass.states.async_set("tuya_vacuum_maps.world", "Mars")
    await hass.config_entries.async_forward_entry_setups(config, [Platform.CAMERA])

    return True
