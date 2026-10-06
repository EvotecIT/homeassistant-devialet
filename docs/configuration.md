# Configuration and troubleshooting

[Back to the README](../README.md) · [Device support](device-support.md)

## Connect a device

Accept a discovered Devialet device, or choose **Settings → Devices & services →
Add integration → Devialet** and enter its host/IP address.

The default local API port is **80**. Change it only if your device exposes its
IP Control API on another port (valid range: 1–65535). Home Assistant must be able to reach the device
on the local network.

Use **Reconfigure** if the address changes. Reconfiguration checks that the
destination is the same Devialet device.

## Connection and dependencies

The integration talks directly to the device's local IP Control API over HTTP.
It does not require a Devialet account, password, API token, or cloud service.
Keep the device API reachable only on a trusted local network.

The client implementation ships inside `custom_components/devialet/devialet_client`.
The standalone `devialet_client` package re-exports that same implementation.
Home Assistant supplies the shared `aiohttp` session; the HACS manifest does not
install a separate client package. Installing the standalone Python wheel instead
requires Python 3.13 or later and declares `aiohttp>=3.9` as its runtime dependency.

Each configuration entry represents one device. Its controls use Home Assistant's
standard media-player, switch, select, number, and button actions. There are no
additional service actions registered under the `devialet` domain.

## Options

Open the integration's **Configure** dialog.

| Option | Default and purpose |
| --- | --- |
| Polling interval | 5 seconds; accepts 3–60 seconds |
| Create LED and power-management sensor entities | Enabled by default; creates the optional setting sensors |

Saving options reloads the integration. The optional-sensor setting controls
creation of LED mode/control and automatic power-off mode/period sensors. It
does not disable the corresponding controls or stop those settings from being
read during a refresh.

Some technical entities are registered but disabled by default. Enable them from
the device's entity list only when useful. Creating an entity and enabling it on
the dashboard are separate choices.

## Data updates

Home Assistant polls the device's local IP Control API; the integration does not
subscribe to pushed state updates. The default interval is five seconds and can
be changed to 3–60 seconds in **Configure**. Changes made on the speaker or in
another app become visible after a successful poll, so the interval is not a
guaranteed maximum delay when the device or network is slow.

Each refresh reads device and system information, sources, the selected source,
and volume. It also reads night mode, rendering mode, LED mode, and power
management when the reported capabilities allow them. A refresh therefore makes
several HTTP requests. Shorter intervals increase traffic to the speaker.

Successful Home Assistant controls request a refresh. When a refresh fails,
coordinator-backed entities become unavailable and recover after a successful
update. Use the connection checks below before removing the integration.

## Daily controls

Use the media player for the sources and playback operations the device exposes.
Dione-specific switches, selects, and buttons appear where supported. Use the
actual options shown by your device rather than copying labels from another
model.

See [automations](automations.md) for volume and mute examples.

## Remove the integration

In **Settings → Devices & services**, open Devialet, find the device's integration
entry, and choose **Delete** from its menu. Repeat for other configured Devialet
entries if you are removing the integration entirely. This follows
[Home Assistant's standard integration removal](https://www.home-assistant.io/common-tasks/general/#removing-an-integration-instance).

Review automations, scripts, and dashboard cards that refer to the removed
entities. Removing the entry does not rewrite those references or factory-reset
the speaker. This integration uses the local API without a vendor account login,
so there is no cloud authorization to revoke.

To remove the downloaded integration code as well, remove all Devialet entries
first, then remove the repository through HACS and restart Home Assistant. For a
manual installation, remove only `custom_components/devialet` from the Home
Assistant configuration directory and restart. Other custom integrations can
share the parent `custom_components` directory.

The integration does not create its own persistent cache files. Home Assistant
manages configuration entries, entity history, and backups separately; removing
the integration is not a request to purge recorder history or existing backups.

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
