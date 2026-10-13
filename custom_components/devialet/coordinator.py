"""Coordinator for Devialet data updates."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DevialetApiClient
from .const import (
    CONF_PATH,
    CONF_SCAN_INTERVAL,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
)
from .exceptions import DevialetConnectionError, DevialetError
from .models import DevialetSnapshot

_LOGGER = logging.getLogger(__name__)

type DevialetConfigEntry = ConfigEntry["DevialetCoordinator"]


class DevialetCoordinator(DataUpdateCoordinator[DevialetSnapshot]):
    """Coordinate Devialet API updates."""

    config_entry: DevialetConfigEntry

    def __init__(self, hass: HomeAssistant, entry: DevialetConfigEntry) -> None:
        """Initialize the coordinator."""
        session = async_get_clientsession(hass)
        self.client = DevialetApiClient(
            host=entry.data[CONF_HOST],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            path=entry.data.get(CONF_PATH, DEFAULT_PATH),
            session=session,
        )
        self.identity_matches_entry = False
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name="devialet",
            update_interval=timedelta(
                seconds=entry.options.get(
                    CONF_SCAN_INTERVAL,
                    DEFAULT_SCAN_INTERVAL_SECONDS,
                )
            ),
        )

    async def _async_update_data(self) -> DevialetSnapshot:
        """Fetch data from the device."""
        try:
            snapshot = await self.client.async_refresh()
        except DevialetConnectionError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="device_unavailable",
            ) from err
        except DevialetError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="refresh_failed",
            ) from err
        issue_id = f"device_identity_{self.config_entry.entry_id}"
        expected = self.config_entry.unique_id
        self.identity_matches_entry = expected is None or expected in (
            snapshot.device.serial, snapshot.device.device_id,
        )
        if not self.identity_matches_entry:
            ir.async_create_issue(
                self.hass, DOMAIN, issue_id,
                is_fixable=False, severity=ir.IssueSeverity.ERROR,
                translation_key="wrong_device",
            )
            raise ConfigEntryError(
                translation_domain=DOMAIN, translation_key="wrong_device",
            )
        ir.async_delete_issue(self.hass, DOMAIN, issue_id)
        return snapshot
