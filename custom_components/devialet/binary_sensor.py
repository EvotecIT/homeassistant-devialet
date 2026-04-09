"""Binary sensors for Devialet."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import DevialetCoordinatorEntity
from .models import DevialetSnapshot


@dataclass(frozen=True, kw_only=True)
class DevialetBinarySensorDescription(BinarySensorEntityDescription):
    """Description for Devialet binary sensors."""

    value_fn: Callable[[DevialetSnapshot], object]


BINARY_SENSOR_DESCRIPTIONS: tuple[DevialetBinarySensorDescription, ...] = (
    DevialetBinarySensorDescription(
        key="stream_lock",
        name="Stream lock",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (
            data.source_state.stream_lock if data.source_state else None
        ),
    ),
    DevialetBinarySensorDescription(
        key="lossless",
        name="Lossless",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: (
            data.source_state.stream_info.lossless
            if data.source_state and data.source_state.stream_info
            else None
        ),
    ),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet binary sensors."""
    async_add_entities(
        DevialetBinarySensor(entry.runtime_data, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class DevialetBinarySensor(DevialetCoordinatorEntity, BinarySensorEntity):
    """Generic Devialet binary sensor."""

    entity_description: DevialetBinarySensorDescription

    def __init__(
        self, coordinator, description: DevialetBinarySensorDescription
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name

    @property
    def is_on(self) -> bool | None:
        """Return the current binary state."""
        return self.entity_description.value_fn(self.coordinator.data)
