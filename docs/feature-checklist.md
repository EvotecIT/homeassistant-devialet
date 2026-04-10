# Devialet Feature Checklist

This checklist tracks what the repository already covers and what still needs work to reach a fuller Devialet integration.

## Current Working Core

- [x] Zeroconf discovery
- [x] Config flow and options flow
- [x] Single `media_player` entity with source selection
- [x] Volume, mute, play, pause, stop, previous, next, and seek where exposed by the device
- [x] Night mode switch
- [x] Rendering mode select
- [x] Stream and metadata read support in the reusable client
- [x] Reusable `devialet_client` Python package
- [x] HACS-ready packaging and first GitHub release

## High-Priority Next

- [ ] Writable LED controls
  - [ ] expose `ledMode` as a writable Home Assistant entity
  - [ ] decide whether `ledControl` should be a `select` or `switch`
  - [ ] validate payloads on a real Dione before exposing broadly
- [x] Writable power management
  - [x] expose auto power-off enabled/disabled
  - [x] expose auto power-off period
  - [ ] confirm the write payload shape on a live device after the Dione IP is rediscovered
- [x] Bluetooth pairing button or service
  - [x] expose `startAdvertising` safely from Home Assistant
  - [ ] add a user-facing description and warning text

## Feature Discovery / Reverse Engineering

- [ ] Confirm `renderingModesPerSourceType`
- [ ] Confirm `orientation`
- [ ] Confirm `roomCorrection`
- [ ] Confirm `explicitInstallationId`
- [ ] Capture additional official-app traffic while toggling those settings

## Broader Device Coverage

- [ ] Validate support against more Devialet models besides Dione
- [ ] Verify feature gating works correctly on models that do not expose Dione-only capabilities
- [ ] Add fixtures from more than one Devialet family

## Home Assistant Polish

- [ ] Add more dedicated config entities once payloads are known
- [ ] Improve diagnostics to surface capability detection more explicitly
- [ ] Add repair guidance for unsupported or changing device endpoints
- [ ] Consider a button platform if Bluetooth pairing is exposed there

## Nice-to-Have Later

- [ ] Event-driven updates if Devialet exposes a usable push/event mechanism
- [ ] Stronger model capability matrix
- [ ] Separate fixture capture helpers for easier API regression testing
