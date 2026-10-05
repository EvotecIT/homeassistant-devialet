"""Sensor platform for Devialet."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfFrequency, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    CONF_ENABLE_DEVICE_SETTINGS_SENSORS,
    DEFAULT_ENABLE_DEVICE_SETTINGS_SENSORS,
    source_label,
)
from .coordinator import DevialetConfigEntry, DevialetCoordinator
from .entity import DevialetCoordinatorEntity
from .models import DevialetSnapshot

# Coordinator reads are shared; HA limits actions per platform and entry.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class DevialetSensorDescription(SensorEntityDescription):
    """Description for Devialet sensors."""

    value_fn: Callable[[DevialetSnapshot], StateType]


SENSOR_DESCRIPTIONS: tuple[DevialetSensorDescription, ...] = (
    DevialetSensorDescription(
        key="source_type",
        translation_key="source_type",
        icon="mdi:audio-input-stereo-minijack",
        value_fn=lambda data: (
            source_label(data.source_state.source.type)
            if data.source_state and data.source_state.source
            else None
        ),
    ),
    DevialetSensorDescription(
        key="codec",
        translation_key="codec",
        icon="mdi:file-music-outline",
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
        translation_key="channels",
        icon="mdi:surround-sound",
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
        translation_key="sampling_rate",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
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
        translation_key="bit_depth",
        icon="mdi:music-note-plus",
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
        translation_key="led_mode",
        icon="mdi:led-strip-variant",
        value_fn=lambda data: data.led_mode.led_mode if data.led_mode else None,
    ),
    DevialetSensorDescription(
        key="led_control",
        translation_key="led_control",
        icon="mdi:led-on",
        value_fn=lambda data: data.led_mode.led_control if data.led_mode else None,
    ),
    DevialetSensorDescription(
        key="auto_power_off_mode",
        translation_key="auto_power_off_mode",
        icon="mdi:power-sleep",
        value_fn=lambda data: (
            data.power_management.auto_power_off if data.power_management else None
        ),
    ),
    DevialetSensorDescription(
        key="auto_power_off_period",
        translation_key="auto_power_off_period",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: (
            data.power_management.auto_power_off_period
            if data.power_management
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: DevialetConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
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
            and data.led_mode is None
        ):
            continue
        if (
            description.key.startswith("auto_power_off")
            and data.power_management is None
        ):
            continue
        entities.append(DevialetSensor(entry.runtime_data, description))
    async_add_entities(entities)


class DevialetSensor(DevialetCoordinatorEntity, SensorEntity):
    """Generic Devialet sensor."""

    entity_description: DevialetSensorDescription

    def __init__(
        self, coordinator: DevialetCoordinator,
        description: DevialetSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator.data)
