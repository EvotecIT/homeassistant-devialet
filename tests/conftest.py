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
TEST_DEVICE_ID = "00000000-0000-4000-8000-000000000001"
TEST_GROUP_ID = "00000000-0000-4000-8000-000000000002"
TEST_INSTALLATION_ID = "00000000-0000-4000-8000-000000000003"
TEST_SYSTEM_ID = "00000000-0000-4000-8000-000000000004"
TEST_SERIAL = "TEST-DIONE-0001"

DEVICE_PAYLOAD = {
    "availableFeatures": [
        "orientation",
        "roomCorrection",
        "powerManagement",
        "explicitInstallationId",
    ],
    "deviceId": TEST_DEVICE_ID,
    "deviceName": "Dione",
    "firmwareFamily": "DOS",
    "groupId": TEST_GROUP_ID,
    "installationId": TEST_INSTALLATION_ID,
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
    "serial": TEST_SERIAL,
    "setupState": "finalized",
    "systemId": TEST_SYSTEM_ID,
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
            "deviceId": TEST_DEVICE_ID,
            "deviceName": "Dione",
            "isSystemLeader": True,
            "role": "Mono",
            "serial": TEST_SERIAL,
        }
    ],
    "groupId": TEST_GROUP_ID,
    "isGroupLeader": True,
    "systemId": TEST_SYSTEM_ID,
    "systemName": "Dione",
    "systemType": "single",
}

SOURCES_PAYLOAD = {
    "sources": [
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000101",
            "type": "bluetooth",
        },
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000102",
            "streamLockAvailable": False,
            "type": "optical",
        },
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000103",
            "type": "upnp",
        },
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000104",
            "streamLockAvailable": True,
            "type": "hdmi",
        },
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000105",
            "type": "spotifyconnect",
        },
        {
            "deviceId": TEST_DEVICE_ID,
            "sourceId": "00000000-0000-4000-8000-000000000106",
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
        "deviceId": TEST_DEVICE_ID,
        "sourceId": "00000000-0000-4000-8000-000000000104",
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
