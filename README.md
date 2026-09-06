# Devialet for Home Assistant

![Devialet for Home Assistant — illustrative artwork](assets/homeassistant-devialet-social.png)

*Illustrative artwork. Available controls depend on the device and integration support.*

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
[![Validate](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/validate.yml?branch=main&style=for-the-badge&label=Validate)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/validate.yml)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/hassfest.yml?branch=main&style=for-the-badge&label=Hassfest)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/hassfest.yml)

Local-first Devialet support for Home Assistant, focused on reliability, clean setup, and controls that actually match what the speaker exposes on your network.

![Devialet integration overview](assets/devialet-overview.png)

## More for your Home Assistant home

Other projects we maintain for the same setup:

- [Dreame & MOVA mowers](https://github.com/EvotecIT/homeassistant-dreamelawnmower) — mowing controls, maps, schedules, and supported cameras.
- [Lawn Mower Card](https://github.com/EvotecIT/lovelace-lawn-mower-card) — a visual dashboard for mower state, maps, and controls.
- [KEF](https://github.com/EvotecIT/homeassistant-kef) — local control for modern and legacy speaker families.
- [Siegenia](https://github.com/EvotecIT/homeassistant-siegenia) — local control for supported window controllers.
- [EasyControlX](https://github.com/EvotecIT/homeassistant-easycontrolx) — connect supported Windows and macOS hosts.

Prefer a native app for everyday control? [CasaRay](https://casaray.dev/)
brings rooms, devices, cameras, and home activity together on iPhone, iPad, and
Mac. [Tactra Remote](https://tactra.dev/) puts media players, speakers, and TV
controls in a focused remote for iPhone, iPad, Apple Watch, and Mac.

Both connect to your Home Assistant setup. Neither is required to use this
project.

## 🎯 What This Is

This project is a custom Home Assistant integration for Devialet speakers that expose the local IP Control API.

Today the strongest real-world validation is on:

- Devialet Dione

The goal is broader Devialet support over time, while keeping the integration stable and practical for everyday Home Assistant use.

## ✨ What You Get

- local discovery and config flow setup
- media player controls
- source selection
- volume and mute
- Dione features such as `night mode`, `rendering mode`, `LED mode`, working auto power-off controls, and Bluetooth pairing
- useful diagnostics and stream metadata, registered but disabled by default when the data is mostly technical
- capability details exposed on the media player for troubleshooting and model-specific support

## 🏠 Installation

### HACS

Click the button below to open this repository in HACS without guessing the owner, repository name, or category:

[![Open your Home Assistant instance and open this repository inside HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=EvotecIT&repository=homeassistant-devialet&category=integration)

After HACS installs the integration and Home Assistant has restarted, start setup here:

[![Open your Home Assistant instance and start setting up Devialet.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=devialet)

Manual HACS path:

1. Open HACS.
2. Add `https://github.com/EvotecIT/homeassistant-devialet` as a custom repository of type `Integration`.
3. Install `Devialet`.
4. Restart Home Assistant.
5. Go to `Settings -> Devices & services` and add `Devialet`.

### Manual

1. Copy the `custom_components/devialet` folder into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from `Settings -> Devices & services`.

## ✅ Current Status

- best support today: Devialet Dione
- local API confirmed against Dione firmware `2.20.1`
- feature-aware refresh avoids querying Dione-only settings on models that do
  not advertise them, while older devices without capability metadata retain
  best-effort probing
- temporary network/device outages mark entities unavailable and recover on a
  later successful poll
- test coverage runs on Python 3.13 and the current Python 3.14 Home Assistant
  stack
- structured so more Devialet models can be added as we confirm their local behavior

The current investigation notes are in `docs/devialet-dione-investigation.md`.

Feature tracking checklist: `docs/feature-checklist.md`

## 🧱 Reusable Python Package

This repository now ships two usable layers:

- `devialet_client` for direct Python access to the local Devialet IP Control API
- the Home Assistant integration in `custom_components/devialet`

Library docs: `docs/python-library.md`

Runnable example: `examples/python_client.py`

Example:

```python
from aiohttp import ClientSession
from devialet_client import DevialetApiClient

async with ClientSession() as session:
    client = DevialetApiClient("192.168.1.10", session)
    snapshot = await client.async_refresh()
    print(snapshot.device.device_name)
```

That means the protocol layer is reusable outside Home Assistant for scripts, tooling, or future apps, while the integration stays focused on Home Assistant UX.

## 🛣️ Roadmap

- next tracked work lives in `docs/feature-checklist.md`
- top priorities are the remaining Dione-only settings and broader non-Dione validation
- broader model validation remains important beyond Dione

## 🛠️ Development

```bash
python -m pip install -e .[test]
ruff check .
python -m compileall devialet_client custom_components tests examples
pytest
```

Note:

- the full Home Assistant pytest stack runs best in Linux CI
- on Windows, `pytest-homeassistant-custom-component` imports `fcntl`, so complete local HA pytest runs are limited

## ❤️ Support

- Issues: [GitHub Issues](https://github.com/EvotecIT/homeassistant-devialet/issues)
- Source: [GitHub Repository](https://github.com/EvotecIT/homeassistant-devialet)
