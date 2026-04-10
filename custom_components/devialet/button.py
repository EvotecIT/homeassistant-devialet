"""Button platform for Devialet."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .entity import DevialetCoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Devialet buttons."""
    if not any(
        source.type == "bluetooth" for source in entry.runtime_data.data.sources
    ):
        return
    async_add_entities([DevialetBluetoothPairingButton(entry.runtime_data)])


class DevialetBluetoothPairingButton(DevialetCoordinatorEntity, ButtonEntity):
    """Button entity for starting Bluetooth pairing."""

    _attr_name = "Start Bluetooth pairing"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:bluetooth-connect"

    def __init__(self, coordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator, "bluetooth_pairing")

    async def async_press(self) -> None:
        """Start Bluetooth advertising / pairing mode."""
        await self._async_perform(
            self.coordinator.client.async_start_bluetooth_pairing()
        )
