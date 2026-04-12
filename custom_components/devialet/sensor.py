"""Sensor platform for Devialet."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory, UnitOfFrequency, UnitOfTime

from .const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS,
    FEATURE_LED_MODE,
    FEATURE_POWER_MANAGEMENT,
    source_label,
)
from .entity import DevialetCoordinatorEntity
from .models import DevialetSnapshot


@dataclass(frozen=True, kw_only=True)
class DevialetSensorDescription(SensorEntityDescription):
    """Description for Devialet sensors."""

    value_fn: Callable[[DevialetSnapshot], object]


SENSOR_DESCRIPTIONS: tuple[DevialetSensorDescription, ...] = (
    DevialetSensorDescription(
        key="source_type",
        name="Source type",
        value_fn=lambda data: (
            source_label(data.source_state.source.type)
            if data.source_state and data.source_state.source
            else None
        ),
    ),
    DevialetSensorDescription(
        key="codec",
        name="Codec",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: (
            data.source_state.stream_info.codec
            if data.source_state and data.source_state.stream_info
            else None
        ),
    ),
    DevialetSensorDescription(
        key="channels",
        name="Channels",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: (
            data.source_state.stream_info.channels
            if data.source_state and data.source_state.stream_info
            else None
        ),
    ),
    DevialetSensorDescription(
        key="sampling_rate",
        name="Sampling rate",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: (
            data.source_state.stream_info.sampling_rate
            if data.source_state and data.source_state.stream_info
            else None
        ),
    ),
    DevialetSensorDescription(
        key="bit_depth",
        name="Bit depth",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: (
            data.source_state.stream_info.bit_depth
            if data.source_state and data.source_state.stream_info
            else None
        ),
    ),
    DevialetSensorDescription(
        key="led_mode",
        name="LED mode",
        value_fn=lambda data: data.led_mode.led_mode if data.led_mode else None,
    ),
    DevialetSensorDescription(
        key="led_control",
        name="LED control",
        value_fn=lambda data: data.led_mode.led_control if data.led_mode else None,
    ),
    DevialetSensorDescription(
        key="auto_power_off_mode",
        name="Auto power off mode",
        value_fn=lambda data: (
            data.power_management.auto_power_off if data.power_management else None
        ),
    ),
    DevialetSensorDescription(
        key="auto_power_off_period",
        name="Auto power off period",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: (
            data.power_management.auto_power_off_period
            if data.power_management
            else None
        ),
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet sensors."""
    data = entry.runtime_data.data
    enable_device_settings_sensors = entry.options.get(
        CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
        DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS,
    )
    entities: list[SensorEntity] = []
    for description in SENSOR_DESCRIPTIONS:
        if (
            description.key
            in {
                "led_mode",
                "led_control",
                "auto_power_off_mode",
                "auto_power_off_period",
            }
            and not enable_device_settings_sensors
        ):
            continue
        if (
            description.key.startswith("led_")
            and FEATURE_LED_MODE not in data.system.available_features
        ):
            continue
        if (
            description.key.startswith("auto_power_off")
            and FEATURE_POWER_MANAGEMENT not in data.system.available_features
        ):
            continue
        entities.append(DevialetSensor(entry.runtime_data, description))
    async_add_entities(entities)


class DevialetSensor(DevialetCoordinatorEntity, SensorEntity):
    """Generic Devialet sensor."""

    entity_description: DevialetSensorDescription

    def __init__(self, coordinator, description: DevialetSensorDescription) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def native_value(self):
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
