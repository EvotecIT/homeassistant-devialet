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

### Setup or discovery fails

Check the address against your router's current device list and confirm the API
port, normally 80. Test reachability from the network where Home Assistant runs;
a phone reaching the speaker does not prove that Home Assistant can reach it.
If the devices are on different VLANs, check the routing and firewall rules
between them. A successful ping alone does not establish HTTP API availability.

For an HTTP check, the integration reads
`http://<device-address>:<port>/ipcontrol/v1/devices/current`. This is a read-only
device-information endpoint. A timeout or refused connection points to the
address, port, network path or device availability. An HTML page or unrelated
JSON response is not proof that the compatible API is available. See
[device support](device-support.md) for the model limitations.

Automatic discovery uses the device's `_devialet-http._tcp.local.` advertisement.
If discovery is absent, try manual setup with the address and port. Manual setup
can work when multicast discovery does not cross the network boundary, but it
still requires access to the same local HTTP API. Discovery alone does not prove
that every feature is supported.

### An existing entry becomes unavailable

Check whether the speaker's address changed. Use **Reconfigure** on the existing
entry to update its connection settings. A different-device rejection means the
destination does not match the saved identity; check the address rather than
deleting the existing entry to bypass that check. Add a separate entry when
connecting a different speaker.

After a temporary outage, entities recover on a successful poll. Give the device
time to become reachable, then check the integration's log if it remains
unavailable. Repeated failed refreshes do not each produce a new outage message;
one recovery message is logged when communication succeeds. Removing and
recreating the entry is not necessary for normal network recovery.

The local API has no integration username, password or token to renew. A login
page or authentication response at the configured address should prompt a check
of the endpoint and network path, rather than a search for Devialet account
credentials in Home Assistant.

### A control is missing or an action fails

Check the device's entity list for disabled entities and review the optional
setting-sensor option above. An unavailable control differs from a disabled
entity: the former needs successful communication, while the latter needs an
explicit enable action. Controls also depend on the capabilities reported by
the device; enabling an entity cannot add an unsupported API feature.

Use the source and mode choices shown by the current device. If an action is
rejected, note which control failed and whether ordinary state updates still
work. A reachable device can reject an individual operation. If all entities
are unavailable, start with the connection checks instead. Do not repeatedly
send the action while diagnosing an offline device.

### Collect useful diagnostics

From the integration entry's menu, download diagnostics when a device snapshot
is available. Include the model, firmware, integration version, Home Assistant
version, failing action, time of failure and steps to reproduce. State whether
setup, ordinary polling and other controls work. If setup never completes,
include the flow error and relevant log entry instead of expecting a device
snapshot.

The diagnostics handler redacts configured addresses, device identities and
media information without modifying the live state. Review the downloaded file
and any separate logs or screenshots before attaching them to an
[issue](https://github.com/EvotecIT/homeassistant-devialet/issues); that redaction
does not apply automatically to every attachment.
