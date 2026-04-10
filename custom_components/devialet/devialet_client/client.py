"""Async client for the Devialet IP Control API."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping

import aiohttp

from .const import (
    BLUETOOTH_ADVERTISING_ENDPOINT,
    CURRENT_SOURCE_ENDPOINT,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DEVICE_INFO_ENDPOINT,
    LED_MODE_ENDPOINT,
    MUTE_ENDPOINT,
    NEXT_ENDPOINT,
    NIGHT_MODE_ENDPOINT,
    PAUSE_ENDPOINT,
    PLAY_ENDPOINT,
    POSITION_ENDPOINT,
    POWER_MANAGEMENT_AUDIO_ENDPOINT,
    POWER_MANAGEMENT_ENDPOINT,
    PREVIOUS_ENDPOINT,
    RENDERING_MODE_ENDPOINT,
    SOURCE_SELECT_ENDPOINT_TEMPLATE,
    SOURCES_ENDPOINT,
    SYSTEM_INFO_ENDPOINT,
    SYSTEM_VOLUME_ENDPOINT,
    TURN_OFF_ENDPOINT,
    UNMUTE_ENDPOINT,
    VOLUME_ENDPOINT,
)
from .exceptions import DevialetConnectionError, DevialetResponseError
from .models import (
    DevialetDeviceInfo,
    DevialetLedMode,
    DevialetNightMode,
    DevialetPowerManagement,
    DevialetRenderingMode,
    DevialetSnapshot,
    DevialetSource,
    DevialetSourceState,
    DevialetSystemInfo,
    DevialetVolume,
)

_LOGGER = logging.getLogger(__name__)


class DevialetApiClient:
    """Client for Devialet's local IP Control API."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        *,
        port: int = DEFAULT_PORT,
        path: str = DEFAULT_PATH,
        request_timeout: float = 3.0,
    ) -> None:
        """Initialize the client."""
        self._host = host
        self._session = session
        self._port = port
        self._path = path.rstrip("/") or DEFAULT_PATH
        self._request_timeout = request_timeout

    @property
    def host(self) -> str:
        """Return the configured host."""
        return self._host

    @property
    def port(self) -> int:
        """Return the configured port."""
        return self._port

    @property
    def path(self) -> str:
        """Return the configured API path prefix."""
        return self._path

    async def async_refresh(self) -> DevialetSnapshot:
        """Fetch a full snapshot of the current device state."""
        device = DevialetDeviceInfo.from_dict(
            await self._request_json("GET", DEVICE_INFO_ENDPOINT)
        )
        system = DevialetSystemInfo.from_dict(
            await self._request_json("GET", SYSTEM_INFO_ENDPOINT)
        )

        sources_payload = await self._request_json("GET", SOURCES_ENDPOINT)
        sources = tuple(
            DevialetSource.from_dict(item)
            for item in sources_payload.get("sources", [])
            if isinstance(item, dict)
        )

        source_state = await self.async_get_source_state()
        volume = await self.async_get_volume()
        night_mode = await self.async_get_night_mode()
        rendering_mode = await self.async_get_rendering_mode()
        led_mode = await self.async_get_led_mode()
        power_management = await self.async_get_power_management()

        return DevialetSnapshot(
            device=device,
            system=system,
            sources=sources,
            source_state=source_state,
            volume=volume,
            night_mode=night_mode,
            rendering_mode=rendering_mode,
            led_mode=led_mode,
            power_management=power_management,
        )

    async def async_get_source_state(self) -> DevialetSourceState | None:
        """Fetch the current source state."""
        payload = await self._request_optional_json("GET", CURRENT_SOURCE_ENDPOINT)
        if payload is None:
            return None
        return DevialetSourceState.from_dict(payload)

    async def async_get_volume(self) -> DevialetVolume | None:
        """Fetch current volume."""
        payload = await self._request_optional_json("GET", VOLUME_ENDPOINT)
        if payload is None:
            payload = await self._request_optional_json("GET", SYSTEM_VOLUME_ENDPOINT)
        if payload is None:
            return None
        return DevialetVolume.from_dict(payload)

    async def async_get_night_mode(self) -> DevialetNightMode | None:
        """Fetch night mode state if supported."""
        payload = await self._request_optional_json("GET", NIGHT_MODE_ENDPOINT)
        if payload is None:
            return None
        return DevialetNightMode.from_dict(payload)

    async def async_get_rendering_mode(self) -> DevialetRenderingMode | None:
        """Fetch rendering mode state if supported."""
        payload = await self._request_optional_json("GET", RENDERING_MODE_ENDPOINT)
        if payload is None:
            return None
        return DevialetRenderingMode.from_dict(payload)

    async def async_get_led_mode(self) -> DevialetLedMode | None:
        """Fetch LED mode state if supported."""
        payload = await self._request_optional_json("GET", LED_MODE_ENDPOINT)
        if payload is None:
            return None
        return DevialetLedMode.from_dict(payload)

    async def async_get_power_management(self) -> DevialetPowerManagement | None:
        """Fetch power-management settings."""
        payload = await self._request_optional_json("GET", POWER_MANAGEMENT_ENDPOINT)
        if payload is None:
            payload = await self._request_optional_json(
                "GET", POWER_MANAGEMENT_AUDIO_ENDPOINT
            )
        if payload is None:
            return None
        return DevialetPowerManagement.from_dict(payload)

    async def async_set_volume_level(self, volume_level: float) -> None:
        """Set the volume level as a Home Assistant float between 0 and 1."""
        volume_percent = max(0, min(100, round(volume_level * 100)))
        await self._request_json(
            "POST",
            VOLUME_ENDPOINT,
            payload={"volume": volume_percent},
        )

    async def async_volume_up(self) -> None:
        """Raise the volume."""
        await self._request_json("POST", f"{VOLUME_ENDPOINT}Up")

    async def async_volume_down(self) -> None:
        """Lower the volume."""
        await self._request_json("POST", f"{VOLUME_ENDPOINT}Down")

    async def async_mute(self) -> None:
        """Mute the current source."""
        await self._request_json("POST", MUTE_ENDPOINT)

    async def async_unmute(self) -> None:
        """Unmute the current source."""
        await self._request_json("POST", UNMUTE_ENDPOINT)

    async def async_play(self) -> None:
        """Start or resume playback."""
        await self._request_json("POST", PLAY_ENDPOINT)

    async def async_pause(self) -> None:
        """Pause playback."""
        await self._request_json("POST", PAUSE_ENDPOINT)

    async def async_stop(self) -> None:
        """Stop playback by using the pause endpoint."""
        await self.async_pause()

    async def async_next_track(self) -> None:
        """Skip to the next track."""
        await self._request_json("POST", NEXT_ENDPOINT)

    async def async_previous_track(self) -> None:
        """Go to the previous track."""
        await self._request_json("POST", PREVIOUS_ENDPOINT)

    async def async_seek(self, position: int) -> None:
        """Seek within the current source if supported."""
        await self._request_json(
            "POST",
            POSITION_ENDPOINT,
            payload={"position": position},
        )

    async def async_set_night_mode(self, enabled: bool) -> None:
        """Set the current night mode."""
        await self._request_json(
            "POST",
            NIGHT_MODE_ENDPOINT,
            payload={"nightMode": "on" if enabled else "off"},
        )

    async def async_set_rendering_mode(self, mode: str) -> None:
        """Set the current rendering mode."""
        await self._request_json(
            "POST",
            RENDERING_MODE_ENDPOINT,
            payload={"renderingMode": mode},
        )

    async def async_set_power_management(
        self,
        *,
        auto_power_off: str,
        auto_power_off_period: int | None = None,
    ) -> None:
        """Set power-management values using the best-known writable endpoint."""
        payload: dict[str, object] = {"autoPowerOff": auto_power_off}
        if auto_power_off_period is not None:
            payload["autoPowerOffPeriod"] = auto_power_off_period

        try:
            await self._request_json(
                "POST",
                POWER_MANAGEMENT_ENDPOINT,
                payload=payload,
            )
        except DevialetResponseError as err:
            if err.status != 404 and err.code != "NotFound":
                raise
            await self._request_json(
                "POST",
                POWER_MANAGEMENT_AUDIO_ENDPOINT,
                payload=payload,
            )

    async def async_set_auto_power_off_enabled(
        self,
        enabled: bool,
        *,
        current_period: int | None = None,
    ) -> None:
        """Enable or disable automatic power off."""
        await self.async_set_power_management(
            auto_power_off="enabled" if enabled else "disabled",
            auto_power_off_period=current_period,
        )

    async def async_set_auto_power_off_period(
        self,
        period: int,
        *,
        enabled: bool | None = None,
    ) -> None:
        """Set the automatic power-off period in minutes."""
        await self.async_set_power_management(
            auto_power_off="enabled" if enabled is None or enabled else "disabled",
            auto_power_off_period=period,
        )

    async def async_select_source(self, source_id: str) -> None:
        """Select a source by source id."""
        endpoint = SOURCE_SELECT_ENDPOINT_TEMPLATE.format(source_id=source_id)
        await self._request_json("POST", endpoint)

    async def async_turn_off(self) -> None:
        """Turn off the current system."""
        await self._request_json("POST", TURN_OFF_ENDPOINT)

    async def async_start_bluetooth_pairing(self) -> None:
        """Start Bluetooth advertising."""
        await self._request_json("POST", BLUETOOTH_ADVERTISING_ENDPOINT)

    async def _request_optional_json(
        self,
        method: str,
        endpoint: str,
        payload: Mapping[str, object] | None = None,
    ) -> dict[str, object] | None:
        """Request JSON from an optional endpoint."""
        try:
            return await self._request_json(method, endpoint, payload=payload)
        except DevialetResponseError as err:
            if err.status == 404 or err.code == "NotFound":
                return None
            raise

    async def _request_json(
        self,
        method: str,
        endpoint: str,
        payload: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Perform a request and return the JSON body."""
        url = self._build_url(endpoint)
        request_kwargs: dict[str, object] = {
            "allow_redirects": False,
            "timeout": aiohttp.ClientTimeout(total=self._request_timeout),
        }

        if method == "POST":
            request_kwargs["json"] = payload or {}
        elif payload is not None:
            request_kwargs["params"] = payload

        try:
            async with self._session.request(method, url, **request_kwargs) as response:
                response_text = await response.text()
                response_content_type = response.headers.get("Content-Type", "")
        except aiohttp.ClientError as err:
            raise DevialetConnectionError(str(err)) from err
        except TimeoutError as err:
            raise DevialetConnectionError(
                "Request to Devialet device timed out"
            ) from err

        if response.status >= 400:
            if response.status == 404:
                raise DevialetResponseError(
                    "Devialet IP Control API was not found at the configured address",
                    status=response.status,
                )
            raise DevialetResponseError(
                f"Devialet device returned HTTP {response.status}",
                status=response.status,
            )

        if not response_text.strip():
            return {}

        if self._looks_like_web_ui_shell(response_text, response_content_type):
            raise DevialetResponseError(
                (
                    "Devialet host returned the web UI shell instead of the "
                    "IP Control JSON API"
                ),
                status=response.status,
            )

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as err:
            raise DevialetResponseError(
                f"Devialet device returned non-JSON data for {endpoint}",
                status=response.status,
            ) from err

        if not isinstance(data, dict):
            raise DevialetResponseError(
                "Devialet device returned an unexpected payload type",
                status=response.status,
            )

        if "error" in data and isinstance(data["error"], dict):
            error = data["error"]
            error_code = error.get("code")
            raise DevialetResponseError(
                "Devialet device returned an API error",
                status=response.status,
                code=error_code if isinstance(error_code, str) else None,
            )

        _LOGGER.debug("Devialet %s %s -> %s", method, url, data)
        return data

    def _build_url(self, endpoint: str) -> str:
        """Build a full request URL."""
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"http://{self._host}:{self._port}{self._path}{endpoint}"

    @staticmethod
    def _looks_like_web_ui_shell(response_text: str, content_type: str) -> bool:
        """Return whether the response looks like the speaker web UI shell."""
        if "text/html" not in content_type.lower():
            return False

        normalized = response_text.lower()
        return (
            "<!doctype html" in normalized
            and "<app-root" in normalized
            and "<title>webui</title>" in normalized
        )
