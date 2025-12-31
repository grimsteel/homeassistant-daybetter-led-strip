"""Sensor platform for daybetter_led_strip."""

from __future__ import annotations

import logging
import math
from typing import TYPE_CHECKING

from daybetter_led_strip.const import Effect
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    EFFECT_OFF,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.components.light.const import ColorMode, LightEntityFeature
from homeassistant.core import callback
from homeassistant.util.color import brightness_to_value, value_to_brightness

from custom_components.daybetter_led.const import CONF_COLOR_CORRECTION

from .entity import DaybetterLedStripEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DaybetterLedStripCoordinator
    from .models import DaybetterLedStripConfigEntry

_LOGGER = logging.getLogger(__name__)

ENTITY_DESCRIPTIONS = (
    LightEntityDescription(
        key="lights",
        translation_key="rgb_lights",
        icon="mdi:lightbulb",
        has_entity_name=True,
    ),
)

# Light is still on for brightness 0
BRIGHTNESS_RANGE = (0, 100)

SUPPORTED_EFFECTS = [
    EFFECT_OFF,
    "switch_rgb",
    "switch_all",
    "fade_fast",
    "fade_slow",
    "blink_red",
    "blink_green",
    "blink_blue",
    "blink_yellow",
    "blink_teal",
    "blink_purple",
    "blink_white",
    "fade_red_green",
    "fade_red_blue",
    "fade_green_blue",
    "flash_all",
    "flash_red",
    "flash_green",
    "flash_blue",
    "flash_yellow",
    "flash_teal",
    "flash_purple",
    "flash_white",
    "strobe_rgb",
    "strobe_all",
]


def effect_to_effect_str(effect: Effect | None) -> str:
    """Convert Effect enum value to effect string."""
    # we ignore effects up to SWITCH_RGB, +1 for EFFECT_OFF
    if effect is None:
        return EFFECT_OFF
    val = effect - Effect.SWITCH_RGB + 1
    if val <= 0 or val >= len(SUPPORTED_EFFECTS):
        return EFFECT_OFF
    return SUPPORTED_EFFECTS[val]


def effect_str_to_effect(effect_str: str) -> Effect | None:
    """Convert effect string to Effect enum value,, or None if unsupported/off."""
    if effect_str not in SUPPORTED_EFFECTS:
        return None
    val = SUPPORTED_EFFECTS.index(effect_str)
    if val <= 0:
        return None
    return Effect(val + Effect.SWITCH_RGB - 1)


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
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = SUPPORTED_EFFECTS

    def __init__(
        self,
        coordinator: DaybetterLedStripCoordinator,
        entity_description: LightEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_available = self.coordinator.data["connected"]
        if self.coordinator.data["brightness"] is not None:
            # scale brightness
            self._attr_brightness = value_to_brightness(
                BRIGHTNESS_RANGE, self.coordinator.data["brightness"]
            )
        else:
            self._attr_brightness = None
        self._attr_rgb_color = self.coordinator.data["color"]
        self._attr_is_on = self.coordinator.data["on"]
        self._attr_effect = effect_to_effect_str(self.coordinator.data["effect"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003
        """Turn the light on with the given color configuration."""
        device = self.coordinator.config_entry.runtime_data.device

        if not self.is_on:
            await device.set_power(True)

        if ATTR_BRIGHTNESS in kwargs:
            await device.set_brightness(
                math.floor(
                    brightness_to_value(BRIGHTNESS_RANGE, kwargs[ATTR_BRIGHTNESS])
                )
            )

        if ATTR_RGB_COLOR in kwargs:
            await device.set_color(
                kwargs[ATTR_RGB_COLOR],
                # default to True
                color_correction=self.coordinator.config_entry.options.get(
                    CONF_COLOR_CORRECTION,
                    True,
                ),
            )

        if ATTR_EFFECT in kwargs:
            effect = effect_str_to_effect(kwargs[ATTR_EFFECT])
            if effect is not None:
                await device.set_effect(effect)
            else:
                # default to white - no color saved
                await device.set_color((255, 255, 255))

    async def async_turn_off(self) -> None:
        """Turn the light off."""
        return await self.coordinator.config_entry.runtime_data.device.set_power(False)
