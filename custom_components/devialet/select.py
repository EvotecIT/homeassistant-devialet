"""Select entities for Devialet."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity

from .const import FEATURE_RENDERING_MODE
from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet selects."""
    entities: list[SelectEntity] = []
    if FEATURE_RENDERING_MODE in entry.runtime_data.data.system.available_features:
        entities.append(DevialetRenderingModeSelect(entry.runtime_data))
    async_add_entities(entities)


class DevialetRenderingModeSelect(DevialetCoordinatorEntity, SelectEntity):
    """Select entity for rendering mode."""

    _attr_name = "Rendering mode"

    def __init__(self, coordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "rendering_mode")

    @property
    def options(self) -> list[str]:
        """Return selectable rendering modes."""
        rendering_mode = self.coordinator.data.rendering_mode
        if rendering_mode is None:
            return []
        return list(rendering_mode.available_rendering_modes)

    @property
    def current_option(self) -> str | None:
        """Return the active rendering mode."""
        rendering_mode = self.coordinator.data.rendering_mode
        if rendering_mode is None:
            return None
        return rendering_mode.rendering_mode

    async def async_select_option(self, option: str) -> None:
        """Change the rendering mode."""
        await self._async_perform(
            self.coordinator.client.async_set_rendering_mode(option)
        )
