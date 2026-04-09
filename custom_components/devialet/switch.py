"""Switch platform for Devialet."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .const import FEATURE_NIGHT_MODE
from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet switches."""
    entities: list[SwitchEntity] = []
    if FEATURE_NIGHT_MODE in entry.runtime_data.data.system.available_features:
        entities.append(DevialetNightModeSwitch(entry.runtime_data))
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
