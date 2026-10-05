# Integration rule ledger

This is Devialet's self-assessment against the [Home Assistant rules](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/),
checked on 2026-10-05. It is an implementation checklist, not an official rating.
The current index contains 54 rules. Every row stays open until the complete
applicable contract has evidence; a source pointer alone is not a pass.

`Partial` identifies existing implementation or focused proof. `Gap` identifies
known missing work. `Review` requires an applicability or contract audit. An
exemption needs the rule's permitted reason and product-specific evidence.

## Bronze

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| action-setup | Review | Entity actions use HA platforms; confirm whether custom action registration is applicable. |
| appropriate-polling | Partial | Coordinator scan options exist; document and measure the request budget for all enabled endpoints. |
| brands | Partial | Local `brand/` assets exist; verify rendered HACS/HA assets and applicable custom-integration requirements. |
| common-modules | Partial | `entity.py`, `coordinator.py`, and `devialet_client/` own shared behaviour; inspect remaining adapter duplication. |
| config-flow-test-coverage | Partial | All 94 executable flow statements and 20 branches are covered by public HA flow tests, including connection/identity failures, discovery, duplicate prevention, reconfiguration, and options. Release-scoped qualification remains open. |
| config-flow | Partial | Manual and discovered setup exist; prove the installed artifact's UI flow. |
| dependency-transparency | Review | Document bundled client ownership, transport, and requirements from the shipped manifest. |
| docs-actions | Review | Reconcile platform actions and automation examples with supported device operations. |
| docs-triggers | Review | Audit custom trigger support and document supported automation usage or applicability. |
| docs-conditions | Review | Audit custom condition support and document supported automation usage or applicability. |
| docs-high-level-description | Partial | README describes speaker control; reconcile it with verified model support. |
| docs-installation-instructions | Partial | README installation path exists; install the actual HACS artifact. |
| docs-removal-instructions | Review | Verify entry removal and HACS uninstall guidance, including retained data. |
| entity-event-setup | Partial | Public HA tests verify repeated reloads keep entity IDs stable and detach old coordinators; platform-forwarding failure can retry with a fresh owner. Installed-host qualification remains open. |
| entity-unique-id | Partial | Entity base supplies identity; verify uniqueness and persistence across migration/reconfiguration. |
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
| docs-configuration-parameters | Partial | Configuration guide exists; reconcile all options, defaults, ranges, and effects. |
| docs-installation-parameters | Partial | Configuration guide exists; reconcile setup fields, credentials, and network prerequisites. |
| entity-unavailable | Partial | Coordinator drives availability; verify offline startup, disconnect, recovery, and dependent entities. |
| integration-owner | Partial | Manifest names maintainers and issue tracker; confirm support and security-reporting paths. |
| log-when-unavailable | Review | Exercise one disconnect/reconnect cycle and inspect logs for useful, non-repeating messages. |
| parallel-updates | Partial | Writable platforms declare `PARALLEL_UPDATES = 1`; coordinator-only sensors declare zero. A real HA multi-entity switch action proves serialization. This is per platform/entry, not a global client lock; see the minimum-version limitation in the development guide. |
| reauthentication-flow | Review | The local IP Control API has no credential field; verify applicability and document the permitted exemption. |
| test-coverage | Gap | The measured baseline at 29391a9 has integration/client statement coverage of 95.5% (965/1010); branch coverage is 79.4% (135/170). The flow has 100% statement and branch coverage. Above 95% module coverage remains a target. |

## Gold

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| devices | Partial | Entity device metadata exists; verify grouping and serial/device-ID fallback across supported models. |
| diagnostics | Partial | Privacy and nonmutation tests pass; inspect the downloaded artifact and all supported model payloads. |
| discovery-update-info | Partial | Zeroconf update handling exists; verify address changes preserve identity and credentials. |
| discovery | Partial | Zeroconf manufacturer matching exists; test model matching and unrelated-device rejection. |
| docs-data-update | Review | Describe polling, update intervals, unavailable states, and expected state delays. |
| docs-examples | Partial | Automation guide exists; validate examples against current entities/actions. |
| docs-known-limitations | Partial | Device-support and Dione investigation notes exist; reconcile protocol and feature restrictions with evidence. |
| docs-supported-devices | Partial | Device support guide exists; distinguish tested hardware from protocol-based expectations. |
| docs-supported-functions | Partial | Feature checklist exists; reconcile platforms and per-model capability gating. |
| docs-troubleshooting | Review | Cover connection, authentication, discovery, diagnostics, and recovery with actionable steps. |
| docs-use-cases | Partial | Automation examples exist; verify complete user workflows. |
| dynamic-devices | Review | Verify applicability for one local device/system per entry and document any permitted exemption. |
| entity-category | Partial | Entity metadata exists; audit configuration and diagnostic categories across platforms. |
| entity-device-class | Partial | Sensor metadata exists; audit classes, units, and state classes across models. |
| entity-disabled-by-default | Partial | Diagnostic sensors and the device-settings option exist; verify useful defaults and user opt-in behaviour. |
| entity-translations | Partial | All 17 child entities use HA translation keys with English and Polish names. Real HA tests verify translated names, English fallback, unchanged primary-device naming, and preservation of existing entity IDs and user overrides. Frontend and released-artifact qualification remain open. |
| exception-translations | Partial | Action connection/rejection failures, unknown sources, and coordinator refresh failures use HA exception keys with English and Polish messages. Public HA service/coordinator tests verify metadata, placeholders, English fallback, and unavailable-state behavior. Raw client details remain in exception causes rather than displayed messages. Rendered frontend and installed-artifact proof remain open. |
| icon-translations | Gap | Add applicable state-aware icon definitions and verify them against entity states. |
| reconfiguration-flow | Partial | Reconfigure step exists; verify identity checks, address changes, and retained settings. |
| repair-issues | Review | Identify failures requiring user intervention and implement applicable repairs without log-only dead ends. |
| stale-devices | Review | Audit the legacy media-player migration, registry removal, and single-entry ownership. |

## Platinum

| Rule | State | Evidence and next acceptance step |
| --- | --- | --- |
| async-dependency | Partial | Bundled client uses async transports; inspect blocking calls, cancellation, and resource lifetime. |
| inject-websession | Partial | Setup and flow use HA's shared session. Local HTTP tests preserve caller ownership and verify status/decompression overrides on borrowed sessions; remaining path and artifact qualification stays open. |
| strict-typing | Partial | mypy 2.4.0 strict checking covers all 21 production modules including the bundled client; current-stable CI enforces the gate. Release-scoped qualification remains open. |

## Qualification beyond the rule ledger

- [x] 116 tests pass on HA 2025.1.0 and HA 2026.9.4 with the same source.
- [ ] Install the published artifact and upgrade from the previous stable release.
- [ ] Verify real model/firmware behaviour, resource use, reconnection, and supported actions.
- [ ] Record release version, commit, artifact identity, environment, and evidence date.

The [development guide](development.md) describes the current focused proof. A completed
row must link the relevant test, artifact, or runtime evidence and state its limits.
