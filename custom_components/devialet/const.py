"""Constants for the Devialet integration."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

DOMAIN = "devialet"
MANUFACTURER = "Devialet"

DEFAULT_PORT = 80
DEFAULT_PATH = "/ipcontrol/v1"
DEFAULT_SCAN_INTERVAL_SECONDS = 5
MIN_SCAN_INTERVAL_SECONDS = 3
MAX_SCAN_INTERVAL_SECONDS = 60

CONF_PATH = "path"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ENABLE_STREAM_DIAGNOSTICS = "enable_stream_diagnostics"
CONF_ENABLE_DEVICE_SETTINGS_SENSORS = "enable_device_settings_sensors"

DEFAULT_ENABLE_STREAM_DIAGNOSTICS = True
DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS = True

DEVICE_INFO_ENDPOINT = "/devices/current"
SYSTEM_INFO_ENDPOINT = "/systems/current"
SOURCES_ENDPOINT = "/groups/current/sources"
CURRENT_SOURCE_ENDPOINT = "/groups/current/sources/current"
VOLUME_ENDPOINT = "/groups/current/sources/current/soundControl/volume"
SYSTEM_VOLUME_ENDPOINT = "/systems/current/sources/current/soundControl/volume"
POSITION_ENDPOINT = "/groups/current/sources/current/playback/position"
NIGHT_MODE_ENDPOINT = "/systems/current/settings/audio/nightMode"
RENDERING_MODE_ENDPOINT = "/systems/current/settings/audio/renderingMode"
LED_MODE_ENDPOINT = "/systems/current/settings/ledMode"
POWER_MANAGEMENT_ENDPOINT = "/systems/current/settings/powerManagement"
POWER_MANAGEMENT_AUDIO_ENDPOINT = "/systems/current/settings/audio/powerManagement"

PLAY_ENDPOINT = "/groups/current/sources/current/playback/play"
PAUSE_ENDPOINT = "/groups/current/sources/current/playback/pause"
NEXT_ENDPOINT = "/groups/current/sources/current/playback/next"
PREVIOUS_ENDPOINT = "/groups/current/sources/current/playback/previous"
MUTE_ENDPOINT = "/groups/current/sources/current/playback/mute"
UNMUTE_ENDPOINT = "/groups/current/sources/current/playback/unmute"
TURN_OFF_ENDPOINT = "/systems/current/powerOff"
BLUETOOTH_ADVERTISING_ENDPOINT = "/systems/current/bluetooth/startAdvertising"

SOURCE_SELECT_ENDPOINT_TEMPLATE = "/groups/current/sources/{source_id}/playback/play"

FEATURE_NIGHT_MODE = "nightMode"
FEATURE_RENDERING_MODE = "renderingMode"
FEATURE_LED_MODE = "ledMode"
FEATURE_POWER_MANAGEMENT = "powerManagement"

SOURCE_LABELS = {
    "airplay2": "AirPlay 2",
    "bluetooth": "Bluetooth",
    "digital_left": "Digital left",
    "digital_right": "Digital right",
    "hdmi": "HDMI",
    "line": "Line",
    "optical": "Optical",
    "opticaljack": "Optical jack",
    "phono": "Phono",
    "raat": "Roon Ready",
    "spotifyconnect": "Spotify Connect",
    "upnp": "UPnP",
}


def source_label(source_type: str) -> str:
    """Return a friendly label for a source type."""
    return SOURCE_LABELS.get(source_type, source_type.replace("_", " ").title())


def build_source_option_map(
    source_types: Iterable[tuple[str, str]],
) -> dict[str, str]:
    """Build a stable label-to-source-id map for Home Assistant source selection."""
    counts = Counter(source_type for source_type, _ in source_types)
    options: dict[str, str] = {}

    for source_type, source_id in source_types:
        label = source_label(source_type)
        if counts[source_type] > 1:
            label = f"{label} ({source_id[:8]})"
        options[label] = source_id

    return dict(sorted(options.items(), key=lambda item: item[0].lower()))
