# Development

[Back to the README](../README.md) · [Python library](python-library.md) ·
[Open work](feature-checklist.md)

```bash
python -m pip install -e .[test]
ruff check .
python -m mypy --strict custom_components/devialet
python -m compileall devialet_client custom_components tests examples
pytest
```

Diagnostics tests verify redaction of device/source identifiers, private names,
media metadata, and artwork URLs while retaining technical state. The source
list is converted from a tuple before HA's recursive redactor runs, so identifiers
inside it are covered too. Tests also verify that downloads do not mutate the
config entry or coordinator snapshot.

For measured integration and bundled-client coverage, run
`pytest --cov=custom_components.devialet --cov-report=term-missing`.
Strict mypy 2.4.0 checking covers all 21 production modules, including the bundled
client. Config-flow statement and branch coverage are both 100%. Above 95%
integration-module coverage and
artifact/device qualification remain open in the [rule ledger](quality.md).

Network tests verify IPv4, DNS names, and IPv6 request URLs, including the device
registry's configuration link. The reusable client owns URL formatting so the
integration and standalone callers share the same behavior. Setup and
reconfiguration forms reject out-of-range ports before network validation.

Writable entity platforms use `PARALLEL_UPDATES = 1`; sensor and binary-sensor
platforms use zero because the coordinator owns their reads. A multi-entity HA
switch action verifies one active write at a time within that platform and entry.
This does not serialize different platforms or coordinator polling. HA 2025.1
bypasses its platform action semaphore for a single-entity service call; current
HA applies it. The integration does not provide a separate global request lock.

Action tests exercise real HA services through the HTTP request boundary for
playback, volume, source selection, LED/rendering modes, night mode, power
management, and Bluetooth pairing. Source options retain friendly names when
built from an iterator. Same-type sources use full IDs when their abbreviated
IDs collide, so every option remains selectable. Unknown sources raise HA's
user-action validation error without sending a write.

Local HTTP tests exercise shared sessions with automatic status raising or
decompression disabled. The client selects its own request policy so optional
endpoint fallback and JSON decoding remain consistent, while leaving the
caller's session open. These tests use loopback servers; they do not establish
physical-speaker behavior.

Lifecycle tests use public HA entry operations to verify offline-startup retry,
failed unload retaining its coordinator and borrowed session, retry after failed
platform forwarding, and repeated reloads preserving registry identities while
detaching old coordinators. HA 2025.1 retains the loaded state after a failed
unload; current HA marks it failed. Both retain the integration owner.

Entity names use HA translation keys with English and Polish labels. Host tests
verify all 17 child entities, English fallback for an untranslated language,
primary-device naming, and existing registry IDs and user names. These are
backend host tests; frontend rendering remains part of artifact qualification.

Note:

- the full Home Assistant pytest stack runs best in Linux CI
- on Windows, `pytest-homeassistant-custom-component` imports `fcntl`, so complete local HA pytest runs are limited

Keep Home Assistant setup and daily-use instructions in the README and user
guides. Protocol investigations and model-validation evidence belong in the
existing investigation notes.

The reusable client is the protocol owner; the Home Assistant integration
provides setup, entities, and automations. See the
[Python library guide](python-library.md) and
[runnable client example](../examples/python_client.py) instead of copying
protocol calls into Home Assistant configuration.

CI tests the declared HA 2026.7.2 minimum and HA 2026.9.4 stable on Python 3.14.
Install `requirements-test-minimum.txt` to reproduce the minimum lane in a separate
virtual environment. Home Assistant supplies its compatible patched DNS and
zeroconf dependencies. Strict typing runs against current stable HA.
