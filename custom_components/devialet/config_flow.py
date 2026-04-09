"""Config flow for Devialet."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .api import DevialetApiClient
from .const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    CONF_ENABLE_STREAM_DIAGNOSTICS,
    CONF_PATH,
    CONF_SCAN_INTERVAL,
    DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS,
    DEFAULT_ENABLE_STREAM_DIAGNOSTICS,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    MAX_SCAN_INTERVAL_SECONDS,
    MIN_SCAN_INTERVAL_SECONDS,
)
from .exceptions import DevialetError


class DevialetConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Devialet config flow."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return DevialetOptionsFlow(config_entry)

    def __init__(self) -> None:
        """Initialize the flow."""
        self._host = ""
        self._port = DEFAULT_PORT
        self._path = DEFAULT_PATH
        self._serial: str | None = None
        self._title = "Devialet"
        self._errors: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle manual setup."""
        self._errors = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._path = DEFAULT_PATH
            result = await self._async_validate_and_create_entry()
            if result is not None:
                return result

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                }
            ),
            errors=self._errors,
        )

    async def async_step_zeroconf(self, discovery_info: ZeroconfServiceInfo):
        """Handle zeroconf discovery."""
        properties = discovery_info.properties
        if properties.get("manufacturer") != "Devialet":
            return self.async_abort(reason="unsupported")

        self._host = discovery_info.host
        self._port = discovery_info.port or DEFAULT_PORT
        self._path = properties.get("path", DEFAULT_PATH)
        self._serial = properties.get("serialNumber")
        self._title = discovery_info.name.removesuffix(f".{discovery_info.type}")

        if self._serial is not None:
            await self.async_set_unique_id(self._serial)
            self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {"title": self._title}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None):
        """Confirm a discovered device."""
        self._errors = {}

        if user_input is not None:
            result = await self._async_validate_and_create_entry()
            if result is not None:
                return result

        return self.async_show_form(
            step_id="confirm", errors=self._errors, last_step=True
        )

    async def _async_validate_and_create_entry(self):
        """Validate the device and create the config entry."""
        session = async_get_clientsession(self.hass)
        client = DevialetApiClient(
            host=self._host,
            port=self._port,
            path=self._path,
            session=session,
        )

        try:
            snapshot = await client.async_refresh()
        except DevialetError:
            self._errors["base"] = "cannot_connect"
            return None

        serial = snapshot.device.serial or snapshot.device.device_id
        if serial is None:
            self._errors["base"] = "unsupported"
            return None

        await self.async_set_unique_id(serial)
        self._abort_if_unique_id_configured()

        title = (
            snapshot.system.system_name or snapshot.device.device_name or self._title
        )
        return self.async_create_entry(
            title=title,
            data={
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_PATH: self._path,
            },
        )


class DevialetOptionsFlow(OptionsFlow):
    """Handle Devialet options."""

    def __init__(self, config_entry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            DEFAULT_SCAN_INTERVAL_SECONDS,
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=MIN_SCAN_INTERVAL_SECONDS,
                            max=MAX_SCAN_INTERVAL_SECONDS,
                        ),
                    ),
                    vol.Optional(
                        CONF_ENABLE_STREAM_DIAGNOSTICS,
                        default=self.config_entry.options.get(
                            CONF_ENABLE_STREAM_DIAGNOSTICS,
                            DEFAULT_ENABLE_STREAM_DIAGNOSTICS,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
                        default=self.config_entry.options.get(
                            CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
                            DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS,
                        ),
                    ): bool,
                }
            ),
        )
