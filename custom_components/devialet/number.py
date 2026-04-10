"""Number entities for Devialet."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import EntityCategory

from .const import FEATURE_POWER_MANAGEMENT
from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet number entities."""
    data = entry.runtime_data.data
    if (
        FEATURE_POWER_MANAGEMENT not in data.system.available_features
        or data.power_management is None
        or data.power_management.auto_power_off_period is None
    ):
        return
    async_add_entities([DevialetAutoPowerOffPeriodNumber(entry.runtime_data)])


class DevialetAutoPowerOffPeriodNumber(DevialetCoordinatorEntity, NumberEntity):
    """Config number for the auto power-off period."""

    _attr_name = "Auto power off period"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:timer-outline"
    _attr_native_min_value = 5
    _attr_native_max_value = 240
    _attr_native_step = 5

    def __init__(self, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, "auto_power_off_period")

    @property
    def native_value(self) -> float | None:
        """Return the current power-off period."""
        power = self.coordinator.data.power_management
        if power is None or power.auto_power_off_period is None:
            return None
        return float(power.auto_power_off_period)

    async def async_set_native_value(self, value: float) -> None:
        """Set the power-off period."""
        power = self.coordinator.data.power_management
        enabled = None if power is None else power.auto_power_off == "enabled"
        await self._async_perform(
            self.coordinator.client.async_set_auto_power_off_period(
                int(value),
                enabled=enabled,
            )
        )
