"""Sensor platform for daybetter_led_strip."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from .entity import DaybetterLedStripEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DaybetterLedStripCoordinator
    from .models import DaybetterLedStripConfigEntry

ENTITY_DESCRIPTIONS: tuple[tuple[SensorEntityDescription, UpdateFn], ...] = (
    (
        SensorEntityDescription(
            key="rssi",
            translation_key="bluetooth_rssi",
            icon="mdi:wifi-strength-2",
            entity_category=EntityCategory.DIAGNOSTIC,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            native_unit_of_measurement="dBm",
            has_entity_name=True,
        ),
        lambda sensor: sensor.coordinator.data["rssi"]
        if sensor.coordinator.data is not None
        else None,
    ),
    (
        SensorEntityDescription(
            key="mac_address",
            translation_key="mac_address",
            icon="mdi:bluetooth",
            entity_category=EntityCategory.DIAGNOSTIC,
            has_entity_name=True,
        ),
        lambda sensor: sensor.coordinator.config_entry.runtime_data.device.address,
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
            update_fn=fn,
        )
        for entity_description, fn in ENTITY_DESCRIPTIONS
    )


class DaybetterLedStripSensor(DaybetterLedStripEntity, SensorEntity):
    """Sensor class."""

    _update_fn: UpdateFn

    def __init__(
        self,
        coordinator: DaybetterLedStripCoordinator,
        entity_description: SensorEntityDescription,
        update_fn: UpdateFn,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description
        self._update_fn = update_fn
        self._attr_native_value = self._update_fn(self)

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_available = self.coordinator.data["connected"]
        self._attr_native_value = self._update_fn(self)
        self.async_write_ha_state()


UpdateFn = Callable[[DaybetterLedStripSensor], Any]
