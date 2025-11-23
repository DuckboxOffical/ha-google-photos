"""Camera platform for Google Photos slideshow."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GooglePhotosAPI
from .const import (
    ATTR_ALBUM_NAME,
    ATTR_CURRENT_PHOTO,
    ATTR_PHOTO_COUNT,
    ATTR_PHOTO_URL,
    CONF_ALBUM_ID,
    CONF_SLIDESHOW_INTERVAL,
    CONF_UPDATE_INTERVAL,
    DEFAULT_SLIDESHOW_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class GooglePhotosCoordinator(DataUpdateCoordinator):
    """Coordinator for Google Photos data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GooglePhotosAPI,
        album_id: str | None,
        update_interval: int,
        slideshow_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api
        self.album_id = album_id
        self.slideshow_interval = slideshow_interval
        self.media_items: list[dict[str, Any]] = []
        self.current_index = 0
        self.album_name: str | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Google Photos."""
        try:
            # Fetch media items
            self.media_items = await self.api.async_list_media_items(self.album_id)

            # Get album name if album_id is set
            if self.album_id:
                albums = await self.api.async_list_albums()
                for album in albums:
                    if album.get("id") == self.album_id:
                        self.album_name = album.get("title", "Unknown Album")
                        break

            if not self.media_items:
                _LOGGER.warning("No media items found")
                return {
                    "photo_url": None,
                    "photo_count": 0,
                    "current_index": 0,
                    "album_name": self.album_name,
                }

            # Ensure current_index is within bounds
            if self.current_index >= len(self.media_items):
                self.current_index = 0

            current_item = self.media_items[self.current_index]
            photo_url = current_item.get("baseUrl", "")

            # Add size parameter for better quality
            if photo_url:
                photo_url += "=w1920-h1080"

            return {
                "photo_url": photo_url,
                "photo_count": len(self.media_items),
                "current_index": self.current_index,
                "album_name": self.album_name,
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching Google Photos data: {err}") from err

    def get_next_photo(self) -> dict[str, Any] | None:
        """Get the next photo in the slideshow."""
        if not self.media_items:
            return None

        self.current_index = (self.current_index + 1) % len(self.media_items)
        current_item = self.media_items[self.current_index]
        photo_url = current_item.get("baseUrl", "")

        if photo_url:
            photo_url += "=w1920-h1080"

        return {
            "photo_url": photo_url,
            "photo_count": len(self.media_items),
            "current_index": self.current_index,
            "album_name": self.album_name,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Google Photos camera from a config entry."""
    api: GooglePhotosAPI = hass.data[DOMAIN][entry.entry_id]

    album_id = entry.options.get(CONF_ALBUM_ID) or entry.data.get(CONF_ALBUM_ID)
    update_interval = entry.options.get(
        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
    )
    slideshow_interval = entry.options.get(
        CONF_SLIDESHOW_INTERVAL, DEFAULT_SLIDESHOW_INTERVAL
    )

    coordinator = GooglePhotosCoordinator(
        hass, api, album_id, update_interval, slideshow_interval
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([GooglePhotosCamera(coordinator, entry)])


class GooglePhotosCamera(Camera):
    """Representation of a Google Photos camera."""

    def __init__(
        self, coordinator: GooglePhotosCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the camera."""
        super().__init__()
        self.coordinator = coordinator
        self._entry = entry
        self._slideshow_task: asyncio.Task | None = None
        self._attr_name = "Google Photos"
        self._attr_unique_id = f"{entry.entry_id}_camera"

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._handle_coordinator_update)
        )
        # Start slideshow task
        self._slideshow_task = asyncio.create_task(self._slideshow_loop())

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        if self._slideshow_task:
            self._slideshow_task.cancel()
            try:
                await self._slideshow_task
            except asyncio.CancelledError:
                pass

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

    async def _slideshow_loop(self) -> None:
        """Loop to advance slideshow."""
        while True:
            try:
                await asyncio.sleep(self.coordinator.slideshow_interval)
                if self.coordinator.media_items:
                    next_photo = self.coordinator.get_next_photo()
                    if next_photo:
                        self.coordinator.async_set_updated_data(next_photo)
            except asyncio.CancelledError:
                break
            except Exception as err:
                _LOGGER.error("Error in slideshow loop: %s", err)
                await asyncio.sleep(5)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        data = self.coordinator.data
        photo_url = data.get("photo_url")

        if not photo_url:
            return None

        try:
            session = self.hass.helpers.aiohttp_client.async_get_clientsession()
            async with session.get(photo_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.read()
        except Exception as err:
            _LOGGER.error("Error fetching photo: %s", err)

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the camera state attributes."""
        data = self.coordinator.data
        return {
            ATTR_PHOTO_COUNT: data.get("photo_count", 0),
            ATTR_CURRENT_PHOTO: data.get("current_index", 0) + 1,
            ATTR_ALBUM_NAME: data.get("album_name"),
            ATTR_PHOTO_URL: data.get("photo_url"),
        }

