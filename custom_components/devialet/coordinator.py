"""Coordinator for Devialet data updates."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DevialetApiClient
from .const import CONF_PATH, DEFAULT_PATH, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL_SECONDS
from .exceptions import DevialetError
from .models import DevialetSnapshot

_LOGGER = logging.getLogger(__name__)

type DevialetConfigEntry = ConfigEntry["DevialetCoordinator"]


class DevialetCoordinator(DataUpdateCoordinator[DevialetSnapshot]):
    """Coordinate Devialet API updates."""

    config_entry: DevialetConfigEntry

    def __init__(self, hass, entry: DevialetConfigEntry) -> None:
        """Initialize the coordinator."""
        session = async_get_clientsession(hass)
        self.client = DevialetApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            path=entry.data.get(CONF_PATH, DEFAULT_PATH),
            session=session,
        )
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="devialet",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )

    async def _async_update_data(self) -> DevialetSnapshot:
        """Fetch data from the device."""
        try:
            return await self.client.async_refresh()
        except DevialetError as err:
            raise UpdateFailed(str(err)) from err
