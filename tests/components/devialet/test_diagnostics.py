"""Privacy contracts for downloaded Devialet diagnostics."""

from dataclasses import asdict
from types import SimpleNamespace

import pytest
from homeassistant.components.diagnostics import REDACTED

from custom_components.devialet.diagnostics import async_get_config_entry_diagnostics
from custom_components.devialet.models import (
    DevialetDeviceInfo,
    DevialetSnapshot,
    DevialetSource,
    DevialetSourceState,
    DevialetSystemInfo,
)
from tests.conftest import DEVICE_PAYLOAD, SYSTEM_PAYLOAD


@pytest.mark.parametrize("with_media", [False, True])
async def test_diagnostics_redact_private_data_without_mutating_state(
    hass, mock_config_entry, with_media
) -> None:
    """Retain useful technical data without names, IDs, or media URLs."""
    source = DevialetSource("private-source-id", "private-device-id", "bluetooth")
    source_state = (
        DevialetSourceState.from_dict(
            {
                "source": {
                    "sourceId": source.source_id,
                    "deviceId": source.device_id,
                    "type": source.type,
                },
                "peerDeviceName": "Personal phone",
                "playingState": "playing",
                "metadata": {
                    "artist": "Private artist",
                    "album": "Private album",
                    "title": "Private recording",
                    "coverArtUrl": "https://example.invalid/art?token=private",
                    "duration": 120,
                    "mediaType": "audio",
                },
                "streamInfo": {"codec": "pcm", "samplingRate": 48000},
            }
        )
        if with_media
        else None
    )
    snapshot = DevialetSnapshot(
        device=DevialetDeviceInfo.from_dict(
            {**DEVICE_PAYLOAD, "deviceName": "Private bedroom"}
        ),
        system=DevialetSystemInfo.from_dict(
            {**SYSTEM_PAYLOAD, "systemName": "Private household"}
        ),
        sources=(source,),
        source_state=source_state,
        volume=None,
        night_mode=None,
        rendering_mode=None,
        led_mode=None,
        power_management=None,
    )
    mock_config_entry.runtime_data = SimpleNamespace(data=snapshot)
    before_entry = mock_config_entry.as_dict()
    before_snapshot = asdict(snapshot)

    result = await async_get_config_entry_diagnostics(hass, mock_config_entry)

    assert result["entry"]["unique_id"] == REDACTED
    assert result["entry"]["title"] == REDACTED
    assert result["entry"]["data"]["host"] == REDACTED
    data = result["snapshot"]
    for key in (
        "device_id",
        "device_name",
        "serial",
        "installation_id",
        "group_id",
        "system_id",
    ):
        assert data["device"][key] == REDACTED
    for key in ("system_id", "system_name", "group_id"):
        assert data["system"][key] == REDACTED
    assert data["device"]["model"] == "Dione"
    assert data["device"]["release"]["version"] == "2.18.6"
    assert data["sources"][0]["source_id"] == REDACTED
    assert data["sources"][0]["device_id"] == REDACTED
    assert data["sources"][0]["type"] == "bluetooth"
    if with_media:
        assert data["source_state"]["peer_device_name"] == REDACTED
        for key in ("artist", "album", "title", "cover_art_url"):
            assert data["source_state"]["metadata"][key] == REDACTED
        assert data["source_state"]["metadata"]["duration"] == 120
        assert data["source_state"]["stream_info"]["codec"] == "pcm"
        assert data["source_state"]["playing_state"] == "playing"
    else:
        assert data["source_state"] is None
    assert mock_config_entry.as_dict() == before_entry
    assert asdict(snapshot) == before_snapshot
