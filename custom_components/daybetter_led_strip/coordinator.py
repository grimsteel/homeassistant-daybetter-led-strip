"""DataUpdateCoordinator for daybetter_led_strip."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .models import DaybetterLedStripState

if TYPE_CHECKING:
    from .models import DaybetterLedStripConfigEntry


class DaybetterLedStripCoordinator(DataUpdateCoordinator):
    """Class to manage pushing data from device."""

    config_entry: DaybetterLedStripConfigEntry

    @callback
    def refresh_state(self) -> None:
        """Refresh the state from the device and push to entities."""
        state = DaybetterLedStripState(
            on=self.config_entry.runtime_data.device.power,
            rssi=self.config_entry.runtime_data.device.rssi,
            color=self.config_entry.runtime_data.device.color,
            brightness=self.config_entry.runtime_data.device.brightness,
        )
        self.async_set_updated_data(asdict(state))
