"""Select entities for Devialet."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import EntityCategory

from .const import FEATURE_LED_MODE, FEATURE_RENDERING_MODE
from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet selects."""
    entities: list[SelectEntity] = []
    data = entry.runtime_data.data
    if FEATURE_RENDERING_MODE in data.system.available_features:
        entities.append(DevialetRenderingModeSelect(entry.runtime_data))
    if FEATURE_LED_MODE in data.system.available_features and data.led_mode is not None:
        entities.append(DevialetLedModeSelect(entry.runtime_data))
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


class DevialetLedModeSelect(DevialetCoordinatorEntity, SelectEntity):
    """Select entity for LED mode."""

    _attr_name = "LED mode"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:led-strip-variant"
    _attr_options = ["auto", "on", "off"]

    def __init__(self, coordinator) -> None:
        """Initialize the select."""
        super().__init__(coordinator, "led_mode_select")

    @property
    def current_option(self) -> str | None:
        """Return the active LED mode."""
        led_mode = self.coordinator.data.led_mode
        if led_mode is None:
            return None
        return led_mode.led_mode

    async def async_select_option(self, option: str) -> None:
        """Change the LED mode."""
        led_mode = self.coordinator.data.led_mode
        current_control = None if led_mode is None else led_mode.led_control
        await self._async_perform(
            self.coordinator.client.async_set_led_mode(
                option,
                led_control=current_control,
            )
        )
