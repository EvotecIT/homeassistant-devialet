# Development

[Back to the README](../README.md) · [Python library](python-library.md) ·
[Open work](feature-checklist.md)

```bash
python -m pip install -e .[test]
ruff check .
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
Full config-flow coverage, above 95% integration-module coverage, strict typing,
and artifact/device qualification remain open quality work.

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
