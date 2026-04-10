"""Protocol constants for the reusable Devialet client."""

from __future__ import annotations

DEFAULT_PORT = 80
DEFAULT_PATH = "/ipcontrol/v1"

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
