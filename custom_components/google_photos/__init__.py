"""The Google Photos integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import GooglePhotosAPI
from .const import DOMAIN
from .options_flow import async_get_options_flow

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CAMERA]

# Register options flow handler
config_entries.HANDLERS.register(DOMAIN)(async_get_options_flow)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Photos from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize the API client
    token = entry.data.get("token", {})
    api = GooglePhotosAPI(
        hass,
        token,
        token.get("refresh_token"),
        entry.data.get("client_id"),
        entry.data.get("client_secret"),
    )

    # Verify we can connect
    try:
        await api.async_verify_access()
    except Exception as err:
        _LOGGER.error("Unable to connect to Google Photos: %s", err)
        raise ConfigEntryNotReady from err

    hass.data[DOMAIN][entry.entry_id] = api

    # Forward the setup to the camera platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

