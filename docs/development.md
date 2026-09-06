# Development

[Back to the README](../README.md) · [Python library](python-library.md) ·
[Open work](feature-checklist.md)

```bash
python -m pip install -e .[test]
ruff check .
python -m compileall devialet_client custom_components tests examples
pytest
```

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
