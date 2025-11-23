"""Config flow for Google Photos integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_CLIENT_ID, CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN, OAUTH_AUTH_URI, OAUTH_TOKEN_URI, SCOPES

_LOGGER = logging.getLogger(__name__)


class GooglePhotosFlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Handle a config flow for Google Photos."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return _LOGGER

    async def async_step_pick_implementation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the implementation pick step."""
        # If flow_impl is already set, proceed directly to auth
        if hasattr(self, "flow_impl") and self.flow_impl:
            return await self.async_step_auth()
        # Otherwise, use the parent implementation
        return await super().async_step_pick_implementation(user_input)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                ),
            )

        if not user_input.get(CONF_CLIENT_ID) or not user_input.get(CONF_CLIENT_SECRET):
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                ),
                errors={"base": "client_id_and_secret_required"},
            )

        # Store credentials temporarily for OAuth flow
        self._client_id = user_input[CONF_CLIENT_ID]
        self._client_secret = user_input[CONF_CLIENT_SECRET]

        # Create the OAuth2 implementation
        try:
            self.flow_impl = GooglePhotosOAuth2Implementation(
                self.hass,
                DOMAIN,
                user_input[CONF_CLIENT_ID],
                user_input[CONF_CLIENT_SECRET],
            )
        except Exception as err:
            _LOGGER.error("Failed to create OAuth2 implementation: %s", err)
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                ),
                errors={"base": "oauth_setup_failed"},
            )

        # Proceed to OAuth authorization step
        try:
            return await self.async_step_pick_implementation_choice()
        except Exception as err:
            _LOGGER.error("OAuth flow error: %s", err, exc_info=True)
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_CLIENT_ID): str,
                        vol.Required(CONF_CLIENT_SECRET): str,
                    }
                ),
                errors={"base": "oauth_flow_error"},
            )

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult:
        """Create an entry for the flow."""
        # Store client_id and client_secret in the entry data
        if hasattr(self, '_client_id') and hasattr(self, '_client_secret'):
            data[CONF_CLIENT_ID] = self._client_id
            data[CONF_CLIENT_SECRET] = self._client_secret
        elif self.flow_impl:
            data[CONF_CLIENT_ID] = self.flow_impl.client_id
            data[CONF_CLIENT_SECRET] = self.flow_impl.client_secret

        return self.async_create_entry(title="Google Photos", data=data)

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reauth upon an API authentication error."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")

        return await self.async_step_user()


class GooglePhotosOAuth2Implementation(
    config_entry_oauth2_flow.LocalOAuth2Implementation
):
    """OAuth2 implementation for Google Photos."""

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Initialize Google Photos OAuth2 implementation."""
        super().__init__(
            hass,
            domain,
            client_id,
            client_secret,
            OAUTH_AUTH_URI,
            OAUTH_TOKEN_URI,
        )
        self._name = "Google Photos"

    @property
    def name(self) -> str:
        """Name of the implementation."""
        return self._name

    @property
    def extra_authorize_data(self) -> dict[str, Any]:
        """Extra data that needs to be appended to the authorize url."""
        return {
            "access_type": "offline",
            "prompt": "consent",
            "scope": " ".join(SCOPES),
        }


