# Device support

[Back to the README](../README.md) · [Configuration](configuration.md)

The integration uses Devialet's local IP Control API. **Dione** has the strongest
real-device validation, including firmware `2.20.1`. That is a recorded test
version, not a minimum or a claim about the latest firmware.

Dione can expose media-player controls, sources, volume, mute, night mode,
rendering mode, LED settings, auto power-off, and Bluetooth pairing.

Other Devialet models need a compatible local API. The integration avoids
requesting Dione-only settings when a device reports that it does not support
them. Older devices without capability metadata use best-effort probing; this
is not a guarantee of complete support.

## Report another model

Include its retail model, firmware, integration version, working and failing
actions, and a reviewed diagnostics capture. Do not infer full compatibility
from successful discovery alone.

Contributor references: [Dione investigation](devialet-dione-investigation.md)
and [open work](feature-checklist.md).
