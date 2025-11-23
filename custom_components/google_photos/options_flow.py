"""Options flow for Google Photos integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback

from .const import (
    CONF_ALBUM_ID,
    CONF_SLIDESHOW_INTERVAL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_SLIDESHOW_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class GooglePhotosOptionsFlowHandler(OptionsFlow):
    """Handle Google Photos options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ALBUM_ID,
                        default=self.config_entry.options.get(
                            CONF_ALBUM_ID, ""
                        ),
                    ): str,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=86400)),
                    vol.Optional(
                        CONF_SLIDESHOW_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SLIDESHOW_INTERVAL, DEFAULT_SLIDESHOW_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=300)),
                }
            ),
        )

