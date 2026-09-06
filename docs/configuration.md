# Configuration and troubleshooting

[Back to the README](../README.md) · [Device support](device-support.md)

## Connect a device

Accept a discovered Devialet device, or choose **Settings → Devices & services →
Add integration → Devialet** and enter its host/IP address.

The default local API port is **80**. Change it only if your device exposes its
IP Control API on another port. Home Assistant must be able to reach the device
on the local network.

Use **Reconfigure** if the address changes. Reconfiguration checks that the
destination is the same Devialet device.

## Options

Open the integration's **Configure** dialog.

| Option | Default and purpose |
| --- | --- |
| Polling interval | 5 seconds; accepts 3–60 seconds |
| Create LED and power-management sensor entities | Enabled by default; creates the optional setting sensors |

Some technical entities are registered but disabled by default. Enable them from
the device's entity list only when useful. Creating an entity and enabling it on
the dashboard are separate choices.

## Daily controls

Use the media player for the sources and playback operations the device exposes.
Dione-specific switches, selects, and buttons appear where supported. Use the
actual options shown by your device rather than copying labels from another
model.

See [automations](automations.md) for volume and mute examples.

## Troubleshooting

- **Cannot connect:** check the device IP, port, and network reachability.
- **Unsupported device:** the endpoint did not provide the expected Devialet IP
  Control API and identity. Check [device support](device-support.md).
- **A setting is missing:** verify that the model advertises it and whether its
  entity is disabled in Home Assistant.
- **Temporarily unavailable:** entities recover after a later successful poll;
  avoid deleting and recreating the integration as a first step.

Reproduce an issue once and download diagnostics from the integration. Include
the model, firmware, integration version, and steps. Review attachments for
personal information before posting.
