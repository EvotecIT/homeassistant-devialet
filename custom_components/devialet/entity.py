"""Shared entity helpers for Devialet."""

from __future__ import annotations

from collections.abc import Awaitable

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import DevialetCoordinator


class DevialetCoordinatorEntity(CoordinatorEntity[DevialetCoordinator]):
    """Base entity for Devialet entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DevialetCoordinator, unique_suffix: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        serial = coordinator.data.device.serial or coordinator.config_entry.entry_id
        self._attr_unique_id = f"{serial}_{unique_suffix}"

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self) -> DeviceInfo:
        """Return device metadata for the entity registry."""
        device = self.coordinator.data.device
        system = self.coordinator.data.system
        return DeviceInfo(
            identifiers={
                (DOMAIN, device.serial or self.coordinator.config_entry.entry_id)
            },
            manufacturer=MANUFACTURER,
            model=device.model or device.model_family,
            model_id=device.device_id,
            name=system.system_name
            or device.device_name
            or self.coordinator.config_entry.title,
            serial_number=device.serial,
            sw_version=device.release.version or device.release.canonical_version,
            configuration_url=(
                f"http://{self.coordinator.client.host}:{self.coordinator.client.port}"
            ),
        )

    async def _async_perform(self, action: Awaitable[object]) -> None:
        """Perform a device action and refresh the coordinator afterwards."""
        await action
        await self.coordinator.async_request_refresh()
