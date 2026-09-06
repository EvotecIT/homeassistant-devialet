# Open Devialet development work

For available controls, use [configuration](configuration.md) and
[device support](device-support.md). The reusable client, Home Assistant
integration, LED and power-management controls, and Bluetooth pairing button
are implemented.

## Device and protocol coverage

- [ ] Validate additional Phantom and other Devialet families with sanitized
  fixtures, especially devices advertising fewer features than Dione.
- [ ] Verify request paths and payloads for `renderingModesPerSourceType`,
  `orientation`, `roomCorrection`, and `explicitInstallationId`.
- [ ] Determine whether `ledControl` needs a separate Home Assistant control
  on devices that distinguish it from `ledMode`.
- [ ] Investigate an event or push mechanism before replacing polling.

The [Dione protocol notes](devialet-dione-investigation.md) retain observed
endpoint and firmware evidence. An advertised feature name alone does not
prove a writable API.

## Home Assistant usability

- [ ] Add clearer guidance for Bluetooth pairing's discoverability window.
- [ ] Add repair guidance for unsupported or changed device endpoints when a
  normal setup error does not explain recovery.

Only add entities for verified capabilities. Factory reset and other destructive
operations must not become ordinary dashboard buttons.
