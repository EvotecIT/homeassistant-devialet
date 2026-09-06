# Devialet Dione protocol notes

These notes retain endpoint and payload findings from April 9, 2026 on Dione
firmware `2.18.6`. Client refresh and capability discovery were rechecked on
July 27, 2026 with firmware `2.20.1`. Those versions describe the captures,
not the latest firmware or current Home Assistant core behavior.

The reusable `devialet_client` and Home Assistant integration are implemented.
See [configuration](configuration.md), [device support](device-support.md), and
the [Python library](python-library.md) for current use.
[Open Devialet development work](feature-checklist.md) tracks the remaining
protocol and device-validation gaps.

## Live Dione findings

The Dione advertised the following during the April capture:

- mDNS service: `_devialet-http._tcp.local.`
- TXT properties:
  - `manufacturer=Devialet`
  - `model=Dione`
  - `firmwareFamily=DOS`
  - `firmwareVersion=2.18.6.49152`
  - `ipControlVersion=1`
  - `path=/ipcontrol/v1`

The integration uses these mDNS properties for discovery.

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

The reusable client models stream information; entities must tolerate missing metadata for sources that do not supply it.

### Observed source inventory

Observed source types:

- `bluetooth`
- `optical`
- `upnp`
- `hdmi`
- `spotifyconnect`
- `airplay2`

Source availability is device-specific; use the returned inventory rather than a fixed Dione list.

### Endpoints not yet confirmed

The device advertises some features that were not found via simple path guessing:

- `renderingModesPerSourceType`
- `orientation`
- `roomCorrection`
- `explicitInstallationId`

Those may still exist behind a different path or request shape.
Capture official-app requests in a supervised session before implementing those settings.

## Capability handling

Use device and system `availableFeatures` before querying optional settings.
Do not assume a Phantom exposes every Dione endpoint, or that an advertised
feature name proves a writable request shape. Keep discovery and API behavior
in the reusable client, with Home Assistant entities consuming its models.
