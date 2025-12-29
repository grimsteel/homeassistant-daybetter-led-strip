"""The led ble integration models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from custom_components.daybetter_led_strip.coordinator import (
        DaybetterLedStripCoordinator,
    )

type DaybetterLedStripConfigEntry = ConfigEntry[DaybetterLedStripData]


@dataclass
class DaybetterLedStripData:
    """Data for the Daybetter LED Strip integration."""

    device: DaybetterLedStrip
    coordinator: DaybetterLedStripCoordinator
    integration: Integration


@dataclass
class DaybetterLedStripState:
    """State for the Daybetter LED Strip integration."""

    on: bool
    color: tuple[int, int, int]
    brightness: int
    rssi: int
