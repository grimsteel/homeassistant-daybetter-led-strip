"""Sensor platform for daybetter_led_strip."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.components.light.const import ColorMode
from homeassistant.core import callback
from homeassistant.util.color import value_to_brightness
from homeassistant.util.percentage import percentage_to_ranged_value

from .entity import DaybetterLedStripEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DaybetterLedStripCoordinator
    from .models import DaybetterLedStripConfigEntry

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="lights",
        name="RGB Lights",
        icon="mdi:lightbulb",
    ),
)

BRIGHTNESS_RANGE = (0, 100)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: DaybetterLedStripConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    async_add_entities(
        DaybetterLedStripLight(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class DaybetterLedStripLight(DaybetterLedStripEntity, LightEntity):
    """RGB Light class."""

    _attr_supported_color_modes = {ColorMode.RGB}  # noqa: RUF012
    _attr_color_mode = ColorMode.RGB

    def __init__(
        self,
        coordinator: DaybetterLedStripCoordinator,
        entity_description: LightEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_brightness = value_to_brightness(
            BRIGHTNESS_RANGE, self.coordinator.data["brightness"]
        )
        self._attr_rgb_color = self.coordinator.data["color"]
        self._attr_is_on = self.coordinator.data["on"]

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003
        """Turn the light on with the given color configuration."""
        if not self.is_on:
            await self.coordinator.config_entry.runtime_data.device.set_power(True)

        if ATTR_BRIGHTNESS in kwargs:
            await self.coordinator.config_entry.runtime_data.device.set_brightness(
                math.floor(
                    percentage_to_ranged_value(
                        BRIGHTNESS_RANGE, kwargs[ATTR_BRIGHTNESS]
                    )
                )
            )

        if ATTR_RGB_COLOR in kwargs:
            await self.coordinator.config_entry.runtime_data.device.set_color(
                kwargs[ATTR_RGB_COLOR]
            )

    async def async_turn_off(self) -> None:
        """Turn the light off."""
        return await self.coordinator.config_entry.runtime_data.device.set_power(False)
