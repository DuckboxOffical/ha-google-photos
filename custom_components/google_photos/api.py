"""API client for Google Photos."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    PICKER_API_BASE,
    PICKER_POLL_ENDPOINT,
    PICKER_SESSION_ENDPOINT,
    SCOPES,
)

_LOGGER = logging.getLogger(__name__)


class GooglePhotosAPI:
    """Google Photos API client."""

    def __init__(
        self,
        hass: HomeAssistant,
        token: dict[str, Any] | None,
        refresh_token: str | None,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.client_id = client_id
        self.client_secret = client_secret
        self._session: aiohttp.ClientSession | None = None
        self._credentials: Credentials | None = None
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None

        if token and refresh_token:
            self._credentials = Credentials(
                token=token.get("access_token"),
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES,
            )
            if token.get("expires_at"):
                self._token_expiry = datetime.fromtimestamp(token["expires_at"])

    async def async_verify_access(self) -> bool:
        """Verify that we can access the API."""
        try:
            await self._ensure_valid_token()
            return True
        except Exception as err:
            _LOGGER.error("Failed to verify access: %s", err)
            return False

    async def _ensure_valid_token(self) -> None:
        """Ensure we have a valid access token."""
        if self._credentials is None:
            raise ValueError("No credentials available")

        # Check if token is expired or will expire soon
        if (
            self._token_expiry is None
            or datetime.now() + timedelta(minutes=5) >= self._token_expiry
        ):
            # Refresh the token
            await self.hass.async_add_executor_job(self._credentials.refresh, Request())
            self._token_expiry = datetime.now() + timedelta(seconds=3600)

        self._access_token = self._credentials.token

    async def async_create_picker_session(
        self, album_id: str | None = None
    ) -> dict[str, Any]:
        """Create a picker session."""
        await self._ensure_valid_token()

        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "featureConfig": {
                "photoPicker": {
                    "enabledFeatures": ["PHOTOS", "ALBUMS"],
                }
            },
        }

        if album_id:
            payload["featureConfig"]["photoPicker"]["albumId"] = album_id

        async with session.post(
            PICKER_SESSION_ENDPOINT, headers=headers, json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to create picker session: {error_text}")

            return await response.json()

    async def async_poll_picker_session(self, session_id: str) -> dict[str, Any]:
        """Poll a picker session to check status."""
        await self._ensure_valid_token()

        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        payload = {"sessionId": session_id}

        async with session.post(
            PICKER_POLL_ENDPOINT, headers=headers, json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to poll picker session: {error_text}")

            return await response.json()

    async def async_get_media_items(self, media_item_ids: list[str]) -> list[dict[str, Any]]:
        """Get media items by their IDs."""
        await self._ensure_valid_token()

        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        payload = {"mediaItemIds": media_item_ids}

        async with session.post(
            f"{PICKER_API_BASE}/mediaItems:batchGet",
            headers=headers,
            json=payload,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Failed to get media items: {error_text}")

            data = await response.json()
            return data.get("mediaItemResults", [])

    async def async_list_albums(self) -> list[dict[str, Any]]:
        """List all albums."""
        await self._ensure_valid_token()

        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        albums = []
        page_token = None

        while True:
            url = f"{PICKER_API_BASE}/albums"
            if page_token:
                url += f"?pageToken={page_token}"

            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Failed to list albums: {error_text}")

                data = await response.json()
                albums.extend(data.get("albums", []))
                page_token = data.get("nextPageToken")

                if not page_token:
                    break

        return albums

    async def async_list_media_items(
        self, album_id: str | None = None, page_size: int = 50
    ) -> list[dict[str, Any]]:
        """List media items, optionally from a specific album."""
        await self._ensure_valid_token()

        session = async_get_clientsession(self.hass)
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        media_items = []
        page_token = None

        while True:
            payload: dict[str, Any] = {"pageSize": page_size}
            if page_token:
                payload["pageToken"] = page_token
            
            # Use albumId filter if provided
            if album_id:
                payload["albumId"] = album_id
            else:
                # For all photos, use filters to get all media items
                payload["filters"] = {
                    "mediaTypeFilter": {
                        "mediaTypes": ["PHOTO"]
                    }
                }

            async with session.post(
                f"{PICKER_API_BASE}/mediaItems:search",
                headers=headers,
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    _LOGGER.error("Failed to list media items: %s", error_text)
                    raise Exception(f"Failed to list media items: {error_text}")

                data = await response.json()
                items = data.get("mediaItems", [])
                if items:
                    media_items.extend(items)
                page_token = data.get("nextPageToken")

                if not page_token:
                    break

        return media_items

    def get_credentials(self) -> Credentials | None:
        """Get the current credentials."""
        return self._credentials

