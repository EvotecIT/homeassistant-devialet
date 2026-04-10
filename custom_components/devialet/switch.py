"""Switch platform for Devialet."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory

from .const import FEATURE_NIGHT_MODE, FEATURE_POWER_MANAGEMENT
from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet switches."""
    entities: list[SwitchEntity] = []
    if FEATURE_NIGHT_MODE in entry.runtime_data.data.system.available_features:
        entities.append(DevialetNightModeSwitch(entry.runtime_data))
    if FEATURE_POWER_MANAGEMENT in entry.runtime_data.data.system.available_features:
        entities.append(DevialetAutoPowerOffSwitch(entry.runtime_data))
    async_add_entities(entities)


class DevialetNightModeSwitch(DevialetCoordinatorEntity, SwitchEntity):
    """Switch entity for night mode."""

    _attr_name = "Night mode"

    def __init__(self, coordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "night_mode")

    @property
    def is_on(self) -> bool | None:
        """Return whether night mode is enabled."""
        night_mode = self.coordinator.data.night_mode
        if night_mode is None:
            return None
        return night_mode.night_mode

    async def async_turn_on(self, **kwargs) -> None:
        """Enable night mode."""
        await self._async_perform(self.coordinator.client.async_set_night_mode(True))

    async def async_turn_off(self, **kwargs) -> None:
        """Disable night mode."""
        await self._async_perform(self.coordinator.client.async_set_night_mode(False))


class DevialetAutoPowerOffSwitch(DevialetCoordinatorEntity, SwitchEntity):
    """Switch entity for automatic power off."""

    _attr_name = "Auto power off"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:power-sleep"

    def __init__(self, coordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "auto_power_off")

    @property
    def is_on(self) -> bool | None:
        """Return whether auto power off is enabled."""
        power_management = self.coordinator.data.power_management
        if power_management is None:
            return None
        return power_management.auto_power_off == "always"

    async def async_turn_on(self, **kwargs) -> None:
        """Enable auto power off."""
        period = (
            self.coordinator.data.power_management.auto_power_off_period
            if self.coordinator.data.power_management
            else None
        )
        await self._async_perform(
            self.coordinator.client.async_set_auto_power_off_enabled(
                True,
                current_period=period,
            )
        )

    async def async_turn_off(self, **kwargs) -> None:
        """Disable auto power off."""
        period = (
            self.coordinator.data.power_management.auto_power_off_period
            if self.coordinator.data.power_management
            else None
        )
        await self._async_perform(
            self.coordinator.client.async_set_auto_power_off_enabled(
                False,
                current_period=period,
            )
        )
