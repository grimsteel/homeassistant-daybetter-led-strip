"""Sensor platform for daybetter_led_strip."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import callback

from .entity import DaybetterLedStripEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DaybetterLedStripCoordinator
    from .models import DaybetterLedStripConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="rssi",
        name="Bluetooth RSSI",
        icon="mdi:network_wifi_2_bar",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: DaybetterLedStripConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        DaybetterLedStripSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class DaybetterLedStripSensor(DaybetterLedStripEntity, SensorEntity):
    """Sensor class."""

    def __init__(
        self,
        coordinator: DaybetterLedStripCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.coordinator.data["rssi"]
