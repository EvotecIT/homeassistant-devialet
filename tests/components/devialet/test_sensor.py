"""Sensor-platform tests for Devialet."""

from __future__ import annotations

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.devialet.sensor import SENSOR_DESCRIPTIONS


def test_every_sensor_has_meaningful_presentation() -> None:
    """New sensors should not fall back to Home Assistant's generic eye icon."""
    assert all(
        description.device_class is not None or description.icon is not None
        for description in SENSOR_DESCRIPTIONS
    )


@pytest.mark.parametrize(
    ("key", "icon", "device_class", "state_class"),
    [
        ("source_type", "mdi:audio-input-stereo-minijack", None, None),
        ("codec", "mdi:file-music-outline", None, None),
        ("channels", "mdi:surround-sound", None, None),
        (
            "sampling_rate",
            None,
            SensorDeviceClass.FREQUENCY,
            SensorStateClass.MEASUREMENT,
        ),
        ("bit_depth", "mdi:music-note-plus", None, None),
        ("led_mode", "mdi:led-strip-variant", None, None),
        ("led_control", "mdi:led-on", None, None),
        ("auto_power_off_mode", "mdi:power-sleep", None, None),
        (
            "auto_power_off_period",
            None,
            SensorDeviceClass.DURATION,
            SensorStateClass.MEASUREMENT,
        ),
    ],
)
def test_sensor_descriptions_have_meaningful_presentation(
    key,
    icon,
    device_class,
    state_class,
) -> None:
    """Each sensor should provide an icon or a semantic device class."""
    description = next(item for item in SENSOR_DESCRIPTIONS if item.key == key)

    assert description.icon == icon
    assert description.device_class == device_class
    assert description.state_class == state_class
