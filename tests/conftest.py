"""Shared test fixtures for the Devialet integration."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.devialet.const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    CONF_PATH,
    DEFAULT_PATH,
    DOMAIN,
)

TEST_HOST = "192.0.2.10"
TEST_PORT = 80
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}{DEFAULT_PATH}"

DEVICE_PAYLOAD = {
    "availableFeatures": [
        "orientation",
        "roomCorrection",
        "powerManagement",
        "explicitInstallationId",
    ],
    "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
    "deviceName": "Dione",
    "firmwareFamily": "DOS",
    "groupId": "e13e163c-bbf6-5912-a77f-44805454c468",
    "installationId": "f07a2da6-4242-5181-8e1c-d0c335b9fd73",
    "ipControlVersion": "1",
    "isSystemLeader": True,
    "model": "Dione",
    "modelFamily": "Dione",
    "release": {
        "buildType": "release",
        "canonicalVersion": "2.18.6.49152",
        "version": "2.18.6",
    },
    "role": "Mono",
    "serial": "Q32Y00392TW1X",
    "setupState": "finalized",
    "systemId": "47366b80-39ea-594a-bad1-37deb6939ce2",
}

SYSTEM_PAYLOAD = {
    "availableFeatures": [
        "nightMode",
        "powerManagement",
        "renderingMode",
        "ledMode",
        "renderingModesPerSourceType",
    ],
    "devices": [
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "deviceName": "Dione",
            "isSystemLeader": True,
            "role": "Mono",
            "serial": "Q32Y00392TW1X",
        }
    ],
    "groupId": "e13e163c-bbf6-5912-a77f-44805454c468",
    "isGroupLeader": True,
    "systemId": "47366b80-39ea-594a-bad1-37deb6939ce2",
    "systemName": "Dione",
    "systemType": "single",
}

SOURCES_PAYLOAD = {
    "sources": [
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "e890b148-43ad-40f5-af06-d6a6c8881d3a",
            "type": "bluetooth",
        },
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "a11d3b06-c2d9-4a15-852f-8173bec0dd75",
            "streamLockAvailable": False,
            "type": "optical",
        },
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "c0b4f9bf-0d6a-4abb-ae1d-4e307f9962bd",
            "type": "upnp",
        },
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "2aa9e81b-90c4-4818-8e41-60eb976d8baf",
            "streamLockAvailable": True,
            "type": "hdmi",
        },
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "2aa14293-aa9e-4ade-ab45-27c89055ea64",
            "type": "spotifyconnect",
        },
        {
            "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
            "sourceId": "31a01794-2ac3-4d31-8aca-cd19dc2834dd",
            "type": "airplay2",
        },
    ]
}

CURRENT_SOURCE_PAYLOAD = {
    "availableOperations": ["play", "pause", "next", "previous"],
    "metadata": {
        "album": "",
        "artist": "",
        "coverArtDataPresent": False,
        "duration": 0,
        "mediaType": "unknown",
        "title": "",
    },
    "muteState": "unmuted",
    "peerDeviceName": "",
    "playingState": "playing",
    "source": {
        "deviceId": "a8be934d-fcdc-56d0-83a1-b51faa98d513",
        "sourceId": "2aa9e81b-90c4-4818-8e41-60eb976d8baf",
        "type": "hdmi",
    },
    "streamInfo": {
        "bitDepth": 16,
        "channels": "5.1.2",
        "codec": "pcm",
        "lossless": False,
        "samplingRate": 48000,
        "supported": True,
    },
    "streamLock": True,
}

VOLUME_PAYLOAD = {"volume": 47}
NIGHT_MODE_PAYLOAD = {"nightMode": "off"}
RENDERING_MODE_PAYLOAD = {
    "availableRenderingModes": ["movie", "music", "voice"],
    "renderingMode": "movie",
}
LED_MODE_PAYLOAD = {"ledControl": "manual", "ledMode": "auto"}
POWER_MANAGEMENT_PAYLOAD = {"autoPowerOff": "disabled", "autoPowerOffPeriod": 90}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable loading custom integrations in tests."""
    yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a sample config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Dione",
        unique_id=DEVICE_PAYLOAD["serial"],
        data={
            "host": TEST_HOST,
            "port": TEST_PORT,
            CONF_PATH: DEFAULT_PATH,
        },
        options={
            CONF_ENABLE_DEVICE_SETTINGS_SENSORS: True,
        },
    )
