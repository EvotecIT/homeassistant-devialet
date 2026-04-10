# Devialet for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://hacs.xyz/)
[![Validate](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/validate.yml?branch=main&style=for-the-badge&label=Validate)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/validate.yml)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/EvotecIT/homeassistant-devialet/hassfest.yml?branch=main&style=for-the-badge&label=Hassfest)](https://github.com/EvotecIT/homeassistant-devialet/actions/workflows/hassfest.yml)

Modern, local-first Devialet support for Home Assistant, built around the Devialet IP Control API and tested against a real Devialet Dione.

## Highlights

- Local polling and zeroconf discovery
- UI config flow and options flow
- Media player controls, source selection, volume, mute
- Dione-focused controls such as `night mode` and `rendering mode`
- Technical stream metadata for diagnostics
- HACS-ready structure with CI and hassfest validation

## Installation

### HACS

1. Open HACS.
2. Add `https://github.com/EvotecIT/homeassistant-devialet` as a custom repository of type `Integration`.
3. Install `Devialet`.
4. Restart Home Assistant.
5. Go to `Settings -> Devices & services` and add `Devialet`.

### Manual

1. Copy [custom_components/devialet](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet) into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from `Settings -> Devices & services`.

## What It Exposes

- `media_player` for playback, source selection, volume, mute, and power
- `switch` for features such as `night mode`
- `select` for configuration such as `rendering mode`
- `sensor` and `binary_sensor` entities for stream and device diagnostics

## Repository Layout

### Reusable Python protocol layer

The reusable Devialet client lives inside the integration today and is designed so it can later be extracted into a standalone Python package:

- [api.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/api.py)
- [models.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/models.py)
- [exceptions.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/exceptions.py)

This layer is responsible for:

- talking to the local Devialet IP Control API
- parsing device, system, source, and stream payloads
- normalizing feature detection for Home Assistant

### Home Assistant integration layer

The Home Assistant integration lives in:

- [config_flow.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/config_flow.py)
- [coordinator.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/coordinator.py)
- [media_player.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/media_player.py)
- [switch.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/switch.py)
- [select.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/select.py)
- [sensor.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/sensor.py)
- [binary_sensor.py](C:/Support/GitHub/homeassistant-devialet/custom_components/devialet/binary_sensor.py)

## Confirmed Device Scope

This repo is currently validated primarily against Devialet Dione firmware `2.18.6`.

Confirmed local endpoints and features are documented in:

- [devialet-dione-investigation.md](C:/Support/GitHub/homeassistant-devialet/docs/devialet-dione-investigation.md)

## Planned Next Steps

- verify and expose more writable Dione settings such as LED and power-management controls
- confirm additional advertised features such as `orientation` and `roomCorrection`
- extract the protocol layer into a reusable standalone Python library when the API surface is stable
- upstream improvements to Home Assistant Core once the behavior is mature enough

## Development

Install test dependencies:

```bash
python -m pip install -e .[test]
```

Run checks:

```bash
ruff check .
python -m compileall custom_components tests
pytest
```

Note:

- the full Home Assistant test harness is Linux-first
- on Windows, `pytest-homeassistant-custom-component` imports `fcntl`, so complete HA pytest runs are expected to execute in CI on Ubuntu

## Support

- Issues: [GitHub Issues](https://github.com/EvotecIT/homeassistant-devialet/issues)
- Source: [GitHub Repository](https://github.com/EvotecIT/homeassistant-devialet)
