# Devialet for Home Assistant

A HACS-ready replacement for Home Assistant's built-in Devialet integration, built around the local Devialet IP Control API.

## Goals

- Work well with current Devialet Dione firmware.
- Stay compatible with Home Assistant setup and entity best practices.
- Keep the API layer modular so it can later be extracted into a standalone Python package or contributed upstream.
- Leave a clean path toward a future iPhone / Apple Watch controller using the same endpoint map.

## Current scope

This initial version focuses on the endpoints confirmed against a live Dione on DOS `2.18.6`:

- media player controls
- source selection
- volume and mute
- night mode
- rendering mode
- stream metadata and technical stream sensors
- LED and power-management readouts

## Not yet exposed

The device advertises additional features that still need endpoint confirmation before they should be surfaced as writable entities:

- `orientation`
- `roomCorrection`
- `explicitInstallationId`
- `renderingModesPerSourceType`

Those are documented in [docs/devialet-dione-investigation.md](C:\Support\GitHub\homeassistant-devialet\docs\devialet-dione-investigation.md).

## Installation with HACS

1. Add this repository as a custom repository in HACS, category `Integration`.
2. Install `Devialet`.
3. Restart Home Assistant.
4. Add the integration from `Settings > Devices & services`.

## Development

Install test dependencies:

```bash
python -m pip install -e .[test]
```

Run tests:

```bash
pytest
```

The full Home Assistant test harness is Linux-first. On Windows, local linting and syntax checks work, but the `pytest-homeassistant-custom-component` plugin imports `fcntl`, so the complete HA test suite is expected to run in CI on Ubuntu.

Lint:

```bash
ruff check .
```
