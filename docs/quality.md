# Integration rule ledger

This is Devialet's self-assessment against the [Home Assistant rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/),
checked on 2026-10-05. It is an implementation checklist, not an official rating.
The current index contains 54 rules. Every row stays open until the complete
applicable contract has evidence; a source pointer alone is not a pass.

Source and compatibility evidence is refreshed on 2026-10-11 against the
maintained HA 2026.7.2 minimum and HA 2026.9.4 comparison target. Older
measurements remain historical unless a row identifies refreshed proof.

`Partial` identifies existing implementation or focused proof. `Gap` identifies
known missing work. `Review` requires an applicability or contract audit. An
exemption needs the rule's permitted reason and product-specific evidence.

## Bronze

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| action-setup | Exempt | No custom service actions are registered. The seven platforms expose standard HA entity actions; `__init__.py` only sets up and unloads platforms. This matches the [no-custom-actions exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/action-setup/#exceptions), checked 2026-10-07. |
| appropriate-polling | Partial | Coordinator scan options exist; document and measure the request budget for all enabled endpoints. |
| brands | Partial | Local `brand/` assets exist; verify rendered HACS/HA assets and applicable custom-integration requirements. |
| common-modules | Partial | `entity.py`, `coordinator.py`, and `devialet_client/` own shared behaviour; inspect remaining adapter duplication. |
| config-flow-test-coverage | Source verified | All 94 executable flow statements and 20 branches are covered on HA 2026.7.2 and 2026.9.4 by public HA flow tests, including connection/identity failures, discovery, duplicate prevention, reconfiguration and options. The measurement retains the coverage tool's two typing-only exclusions and adds no exclusions. Release-scoped qualification remains open. |
| config-flow | Partial | Manual and discovered setup exist; prove the installed artifact's UI flow. |
| dependency-transparency | Source verified | The configuration guide identifies the bundled canonical client, direct local HTTP transport, shared HA aiohttp session, and standalone wheel requirement. Checked against `manifest.json`, `pyproject.toml`, the public re-export package, and the bundled request implementation; no cloud authentication or external client package is required by HACS. |
| docs-actions | Review | Reconcile platform actions and automation examples with supported device operations. |
| docs-triggers | Exempt | The integration registers no custom triggers or device-trigger provider. Automations use HA's standard triggers with the exposed entities, as shown in the [automation guide](automations.md). This matches the [no-provided-triggers exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-triggers/#exceptions), checked against all integration modules on 2026-10-11. |
| docs-conditions | Exempt | The integration registers no custom conditions or device-condition provider. The [automation guide](automations.md) uses HA's standard template condition to check speaker availability. This matches the [no-provided-conditions exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-conditions/#exceptions), checked against all integration modules on 2026-10-11. |
| docs-high-level-description | Partial | README describes speaker control; reconcile it with verified model support. |
| docs-installation-instructions | Partial | README installation path exists; install the actual HACS artifact. |
| docs-removal-instructions | Source verified | Configuration guide covers entry deletion, affected automation/dashboard references, HACS/manual code removal, and retained HA history/backups. The local API needs no cloud authorization revocation; the integration has no private persistent cache. Installed-host removal remains a separate lifecycle qualification gate. |
| entity-event-setup | Partial | Public HA tests verify repeated reloads keep entity IDs stable and detach old coordinators; platform-forwarding failure can retry with a fresh owner. Installed-host qualification remains open. |
| entity-unique-id | Partial | Public HA registry tests verify that migration from the legacy media-player unique ID preserves the entity ID, user name/icon and disabled preference; an existing current entity survives duplicate cleanup, unrelated entities remain, and missing serial identity prevents destructive migration. Repeated reload tests preserve all current entity IDs. Published-artifact upgrades and real models remain separate proof. |
| has-entity-name | Partial | Entity base enables entity names; audit primary and child entity naming. |
| runtime-data | Partial | Entry owns coordinator in `runtime_data`; tests verify offline startup publishes no runtime, failed unload retains its owner, and failed platform forwarding retries with a fresh owner. |
| test-before-configure | Partial | Config flow validates the host; cover all supported transports and failure classes. |
| test-before-setup | Partial | Public HA tests verify offline setup enters retry state without creating entities, then reload succeeds after connection recovery. The local API has no configured authentication. |
| unique-config-entry | Partial | Flow duplicate checks exist; test discovered/manual and changed-address combinations. |

## Silver

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| action-exceptions | Partial | Real HA actions verify HTTP method/path/payload mapping, unknown sources raise ServiceValidationError, and local HTTP tests distinguish unsupported endpoint fallback from server failures. Action and refresh failures carry HA exception translation metadata; installed/frontend qualification stays open. |
| config-entry-unloading | Partial | Public HA tests cover successful unload, failed unload retaining runtime/session ownership, failed platform forwarding, and repeated reload without stale entity updates. Actual host reload qualification remains open. |
| docs-configuration-parameters | Source verified | Guide documents both options, defaults, polling bounds, reload behavior, and which optional sensors are affected; checked against config_flow, constants, update listener, and sensor setup. |
| docs-installation-parameters | Source verified | Guide documents host/address, local reachability, port default/range, discovery, and same-device reconfiguration; checked against the setup/reconfigure schemas. Local API configuration has no credentials or cloud account. |
| entity-unavailable | Partial | Coordinator drives availability; verify offline startup, disconnect, recovery, and dependent entities. |
| integration-owner | Partial | Manifest names maintainers and issue tracker; confirm support and security-reporting paths. |
| log-when-unavailable | Implemented | The public HA outage/recovery test exercises three failed refreshes: one coordinator error is logged, repeated failures do not repeat it, and a successful refresh logs one INFO recovery message while restoring the media-player state. HA owns this transition logging; no duplicate integration logger was added. Physical-device timing remains separate evidence. |
| parallel-updates | Partial | Writable platforms declare `PARALLEL_UPDATES = 1`; coordinator-only sensors declare zero. A real HA multi-entity switch action proves serialization. This is per platform/entry, not a global client lock; see the minimum-version limitation in the development guide. |
| reauthentication-flow | Exempt | Setup/reconfigure accept host and port, and the bundled IP Control client sends local HTTP requests without credentials, tokens, or an authentication exchange. This matches the [no-authentication exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reauthentication-flow/#exceptions), checked 2026-10-07. Address changes use Reconfigure. |
| test-coverage | Source verified | 146 tests pass on HA 2026.7.2 and 2026.9.4. The integration and bundled client cover 1,012/1,020 statements (99.22%) and 168/174 branches (96.55%); combined coverage is 98.83%, with every production module above 95%. Full flow coverage is retained. New proof covers legacy registry migration, optional settings disappearing/recovering, media-state fallback and real local HTTP errors, disconnects, deadlines and cancellation. No exclusions were added. Published-artifact and physical-device qualification remain separate. |

## Gold

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| devices | Partial | Entity device metadata exists; verify grouping and serial/device-ID fallback across supported models. |
| diagnostics | Partial | Privacy and nonmutation tests pass; inspect the downloaded artifact and all supported model payloads. |
| discovery-update-info | Partial | Zeroconf update handling exists; verify address changes preserve identity and credentials. |
| discovery | Partial | Zeroconf manufacturer matching exists; test model matching and unrelated-device rejection. |
| docs-data-update | Source verified | Configuration guide describes local polling, the 5-second default and 3–60-second range, multiple requests per refresh, action-triggered refreshes, state delays, and unavailable/recovery behavior; checked against coordinator, client, and entity action owners. |
| docs-examples | Partial | Automation guide exists; validate examples against current entities/actions. |
| docs-known-limitations | Partial | Device-support and Dione investigation notes exist; reconcile protocol and feature restrictions with evidence. |
| docs-supported-devices | Partial | Device support guide exists; distinguish tested hardware from protocol-based expectations. |
| docs-supported-functions | Partial | Feature checklist exists; reconcile platforms and per-model capability gating. |
| docs-troubleshooting | Source verified | The configuration guide covers local HTTP reachability, the read-only device-information endpoint, multicast discovery versus manual setup, same-device address changes, automatic outage recovery, capability/disabled-entity distinctions, rejected controls, and diagnostics collection. Checked against manifest discovery, config-flow identity checks, coordinator logging, client endpoints/capabilities and diagnostic redaction. Physical network and installed UI qualification remain separate. |
| docs-use-cases | Partial | Automation examples exist; verify complete user workflows. |
| dynamic-devices | Exempt | Each entry owns one coordinator/client and one device identity. All platform entities use the shared entity device metadata; the client returns one device snapshot, not an enumerable child-device collection. This matches the [single-static-device exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/dynamic-devices/#exceptions), checked 2026-10-07. Separate discovered devices receive separate entries. |
| entity-category | Partial | Entity metadata exists; audit configuration and diagnostic categories across platforms. |
| entity-device-class | Partial | Sensor metadata exists; audit classes, units, and state classes across models. |
| entity-disabled-by-default | Partial | Diagnostic sensors and the device-settings option exist; verify useful defaults and user opt-in behaviour. |
| entity-translations | Partial | All 17 child entities use HA translation keys with English and Polish names. Real HA tests verify translated names, English fallback, unchanged primary-device naming, and preservation of existing entity IDs and user overrides. Frontend and released-artifact qualification remain open. |
| exception-translations | Partial | Action connection/rejection failures, unknown sources, and coordinator refresh failures use HA exception keys with English and Polish messages. Public HA service/coordinator tests verify metadata, placeholders, English fallback, and unavailable-state behavior. Raw client details remain in exception causes rather than displayed messages. Rendered frontend and installed-artifact proof remain open. |
| icon-translations | Partial | HA loads icon resources for all custom-icon entities, including on/off states for night mode, automatic power-off, and LED mode. Tests verify registered translation keys and actual entity states on minimum/current HA; the built wheel contains byte-identical icon and English/Polish translation resources. Rendered frontend and installed-artifact qualification remain open. |
| reconfiguration-flow | Partial | Reconfigure step exists; verify identity checks, address changes, and retained settings. |
| repair-issues | Review | Identify failures requiring user intervention and implement applicable repairs without log-only dead ends. |
| stale-devices | Exempt | Each config entry owns one static speaker identity through the shared entity device metadata; there is no hub/account child-device inventory. Removal follows entry deletion, matching the [single-static-device exception](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/stale-devices/#exceptions), checked on 2026-10-11. Legacy media-player entity migration is separately covered by [registry tests](../tests/components/devialet/test_registry_migration.py). |

## Platinum

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| async-dependency | Partial | The bundled client uses aiohttp. Real local HTTP tests verify disconnect/timeout mapping, cancellation propagation and successful requests after failure; no caller session is closed. Resource budgets, physical-network timing and installed-artifact qualification remain open. |
| inject-websession | Partial | Setup and flow use HA's shared session. Local HTTP tests preserve caller ownership, verify status/decompression overrides and reuse the borrowed session after disconnects, deadlines and cancellation. Installed-artifact qualification remains open. |
| strict-typing | Partial | Strict mypy passes all 21 production modules. The standalone wheel includes PEP 561 markers and canonical type re-exports; isolated consumers pass on Python 3.13/3.14 and reject invalid arguments without Home Assistant installed. CI checks the installed contract in both lanes. Published-release qualification remains open. |

## Qualification beyond the rule ledger

- [x] 146 tests pass on the maintained HA 2026.7.2 minimum and HA 2026.9.4 target with the same source; all 21 production files pass strict typing in both environments.
- [ ] Install the published artifact and upgrade from the previous stable release.
- [ ] Verify real model/firmware behaviour, resource use, reconnection, and supported actions.
- [ ] Record release version, commit, artifact identity, environment, and evidence date.

The [development guide](development.md) describes the current focused proof. A completed
row must link the relevant test, artifact, or runtime evidence and state its limits.
