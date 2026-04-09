# Devialet Dione + Home Assistant investigation

Date: 2026-04-09

## Summary

This investigation compared three things:

1. The official Devialet IP Control reference PDF from December 2021.
2. The current Home Assistant Devialet integration and its backing `devialet==1.5.7` library.
3. A live Devialet Dione on firmware `2.18.6`.

Main conclusion:

- The Dione exposes more API surface than Home Assistant currently uses.
- The current Home Assistant integration is structurally sound, but functionally thin.
- The cleanest path is to build a richer reusable client library first, then a Home Assistant custom integration on top of it.

## Official sources

### Devialet IP Control PDF

The official PDF documents:

- Discovery via mDNS and the `path` TXT record.
- Read and write access for:
  - device info
  - system info
  - sources
  - current playback state
  - volume
  - play / pause / mute / next / previous
  - equalizer
  - night mode
  - bluetooth pairing
  - power off / restart / factory reset

Important limitations in the PDF:

- It is revision 1 from December 2021.
- It predates newer Dione-specific features.
- It explicitly allows newer devices to expose additional undocumented fields.

### Devialet Dione release notes

On June 2, 2025, Devialet released Dione firmware `2.18.6`.
The official release notes say:

- Dione can automatically power off after inactivity.
- "The IP Control API now supports all product features."

That line strongly suggests the 2021 PDF is incomplete for current Dione firmware.

## Live Dione findings

The local Dione responds on:

- mDNS service: `_devialet-http._tcp.local.`
- TXT properties:
  - `manufacturer=Devialet`
  - `model=Dione`
  - `firmwareFamily=DOS`
  - `firmwareVersion=2.18.6.49152`
  - `ipControlVersion=1`
  - `path=/ipcontrol/v1`

This means Home Assistant-style zeroconf discovery is viable and a future iOS/watch app should also use mDNS instead of hardcoding IP addresses.

### Confirmed working GET endpoints

- `/ipcontrol/v1/devices/current`
  - returns device metadata and device-level `availableFeatures`
- `/ipcontrol/v1/systems/current`
  - returns system metadata and system-level `availableFeatures`
- `/ipcontrol/v1/groups/current/sources`
  - returns available sources
- `/ipcontrol/v1/groups/current/sources/current`
  - returns active source, playback state, metadata, mute state, stream info, and operations
- `/ipcontrol/v1/groups/current/sources/current/soundControl/volume`
  - returns integer volume
- `/ipcontrol/v1/systems/current/settings/audio/nightMode`
  - returns `nightMode`
- `/ipcontrol/v1/systems/current/settings/audio/renderingMode`
  - returns current rendering mode and allowed values
- `/ipcontrol/v1/systems/current/settings/ledMode`
  - returns LED mode data
- `/ipcontrol/v1/systems/current/settings/powerManagement`
  - returns auto power off data
- `/ipcontrol/v1/systems/current/settings/audio/powerManagement`
  - same data also works on this path
- `/ipcontrol/v1/groups/current/sources/current/playback/position`
  - returns structured API errors like `PositionNotAvailable` when position does not exist

### Observed live response highlights

#### `/systems/current`

Observed `availableFeatures`:

- `nightMode`
- `powerManagement`
- `renderingMode`
- `ledMode`
- `renderingModesPerSourceType`

#### `/devices/current`

Observed `availableFeatures`:

- `orientation`
- `roomCorrection`
- `powerManagement`
- `explicitInstallationId`

#### `/groups/current/sources/current`

Observed fields beyond the older PDF baseline:

- `streamInfo.bitDepth`
- `streamInfo.channels`
- `streamInfo.codec`
- `streamInfo.lossless`
- `streamInfo.samplingRate`
- `streamInfo.supported`
- `streamLock`
- `peerDeviceName`
- `metadata.coverArtDataPresent`

These are especially interesting for Home Assistant sensors and for a future iOS/watch app.

### Confirmed current source inventory on this Dione

Observed source types:

- `bluetooth`
- `optical`
- `upnp`
- `hdmi`
- `spotifyconnect`
- `airplay2`

That confirms Dione source handling is broader than the currently documented Home Assistant tested-model list.

### Endpoints not yet confirmed

The device advertises some features that were not found via simple path guessing:

- `renderingModesPerSourceType`
- `orientation`
- `roomCorrection`
- `explicitInstallationId`

Those may still exist behind a different path or request shape.
If we want full coverage, the next best step is to capture traffic from the official Devialet mobile app while toggling those settings.

## Current Home Assistant state

### Upstream integration behavior

The current Home Assistant Devialet integration:

- creates a single `media_player` entity
- polls every 5 seconds
- uses the external Python library `devialet==1.5.7`
- supports:
  - source select
  - volume
  - mute
  - playback operations
  - equalizer-based sound modes
  - night mode through `sound_mode`
  - power off

### Important gap

The current Python library does not request or expose:

- rendering mode
- LED mode
- power management
- stream info fields
- stream lock
- Dione-specific device settings

So even if Home Assistant wanted to show them, the current client layer does not provide them.

### Documentation mismatch

As of Home Assistant `2026.4.1`, the public integration page still says:

- firmware should be `2.16.1` or later
- known tested models are `Phantom I` and `Phantom II`

That is behind the observed Dione capability surface and behind Devialet's June 2, 2025 release note claim.

## Recommended architecture

## 1. Build a reusable API client first

Create a small standalone client library that models the Dione API explicitly.

Suggested responsibilities:

- device discovery via mDNS
- strongly typed models for device, system, source, source state, stream info, and settings
- feature detection from `availableFeatures`
- safe GET/POST wrappers
- structured error handling
- optional diagnostics snapshot export

Reason:

- the same client can power Home Assistant, scripts, and a future iOS/watch app
- it avoids burying API logic inside Home Assistant entity classes
- it makes testing much easier

## 2. Build the Home Assistant integration on top of that client

Suggested Home Assistant entities:

- `media_player`
  - playback
  - source
  - volume
  - metadata
- `switch`
  - night mode
- `select`
  - rendering mode
  - LED mode
  - maybe source if you want a dedicated selector in addition to `media_player`
- `number` or `select`
  - auto power-off period
- `switch` or `select`
  - auto power-off enabled/disabled
- `sensor`
  - codec
  - channels
  - sample rate
  - bit depth
  - lossless
  - stream lock
  - active source type
- `button`
  - bluetooth pairing

Avoid exposing dangerous operations like factory reset as normal entities.
If ever added, they should be explicit services with strong warnings.

## 3. Keep feature exposure dynamic

Do not hardcode Dione-only assumptions everywhere.

Instead:

- read `availableFeatures`
- create entities only when the feature exists
- tolerate newer response fields
- keep unknown fields in diagnostics

This will make the integration work across Phantom, Dione, and future models.

## 4. Document the API as a product, not just code comments

Recommended outputs:

- a hand-written Markdown reference
- JSON fixtures captured from a real device in several playback states
- a Postman collection or equivalent request examples
- typed model docs that can later be mirrored in Swift

This is better than trying to pretend the device already exposes a formal OpenAPI spec.

## Implementation plan

### Phase 1

- scaffold a repo
- add discovery
- implement typed GET client
- model confirmed endpoints only
- add fixture-based tests using captured JSON

### Phase 2

- build a Home Assistant custom integration
- support `media_player`, night mode, rendering mode, LED mode, and power management
- expose stream info as sensors

### Phase 3

- reverse-engineer the still-missing Dione features
- capture official app traffic while changing orientation and room correction
- add those endpoints once confirmed

### Phase 4

- build a small Swift package for discovery + control
- reuse the same endpoint map and fixtures
- then build the iPhone/watch app UI

## What I would build next

If continuing from this investigation, the best next step is:

1. Initialize a repo in this folder.
2. Create a reusable Python client package for the confirmed endpoints.
3. Add a Home Assistant custom component that uses that client.
4. Capture a few more live fixtures from the Dione for tests.

That gives a clean foundation for both Home Assistant and a later Apple app.
