# Devialet for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
[![Validate](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/validate.yml?branch=main&style=for-the-badge&label=Validate)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/validate.yml)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/hassfest.yml?branch=main&style=for-the-badge&label=Hassfest)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/hassfest.yml)

Local-first Devialet support for Home Assistant, focused on reliability, clean setup, and controls that actually match what the speaker exposes on your network.

![Devialet integration overview](assets/devialet-overview.png)

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
- useful diagnostics and stream metadata

## 🏠 Installation

### HACS

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
- local API confirmed and tested against Dione firmware `2.18.6`
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
