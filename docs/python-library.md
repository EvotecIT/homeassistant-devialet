# Devialet Python Library

`devialet_client` is the reusable async Python layer that powers the Home Assistant integration in this repository.

It is intended for:

- local scripts
- diagnostics and reverse engineering
- future native clients on other platforms
- tests that need a thin API client without booting Home Assistant

## Installation

From this repository:

```bash
python -m pip install -e .
```

## Quick Start

```python
import asyncio

from aiohttp import ClientSession
from devialet_client import DevialetApiClient


async def main() -> None:
    async with ClientSession() as session:
        client = DevialetApiClient("192.168.1.10", session)
        snapshot = await client.async_refresh()
        print(snapshot.device.device_name)
        print(snapshot.system.system_name)
        print(snapshot.volume.level if snapshot.volume else "no volume data")


asyncio.run(main())
```

## Main Workflow

Typical usage looks like this:

1. Create an `aiohttp.ClientSession`
2. Create `DevialetApiClient(host, session, port=80, path="/ipcontrol/v1")`
3. Call `async_refresh()` to get a full `DevialetSnapshot`
4. Use targeted getters or setters for specific actions

## Public Models

The most useful models are:

- `DevialetSnapshot`: one full refresh result
- `DevialetDeviceInfo`: device identity, firmware, serial, release info
- `DevialetSystemInfo`: system/group-level information
- `DevialetSourceState`: current source playback state and metadata
- `DevialetVolume`: current volume and mute information
- `DevialetNightMode`
- `DevialetRenderingMode`
- `DevialetLedMode`
- `DevialetPowerManagement`

## Main Read Methods

- `async_refresh()`: load the current speaker snapshot
- `async_get_source_state()`: current source state only
- `async_get_volume()`: current volume only
- `async_get_night_mode()`
- `async_get_rendering_mode()`
- `async_get_led_mode()`
- `async_get_power_management()`

## Main Control Methods

- `async_set_volume_level(volume_level)`
- `async_volume_up()`
- `async_volume_down()`
- `async_mute()`
- `async_unmute()`
- `async_play()`
- `async_pause()`
- `async_stop()`
- `async_next_track()`
- `async_previous_track()`
- `async_seek(position)`
- `async_select_source(source_id)`

## Dione-Specific / Confirmed Feature Methods

These are especially relevant for Dione and other devices that expose the same local endpoints:

- `async_set_night_mode(enabled)`
- `async_set_rendering_mode(mode)`
- `async_turn_off()`
- `async_start_bluetooth_pairing()`

## Error Handling

The library exposes:

- `DevialetError`: base exception
- `DevialetConnectionError`: transport or connectivity issue
- `DevialetResponseError`: invalid or unexpected device response

## Notes

- This library talks to the local Devialet IP Control API.
- Capability differences between models are real, so callers should prefer checking snapshot fields instead of assuming every method is meaningful on every speaker.
- The Home Assistant integration in `custom_components/devialet` is built on top of this package.
