"""
Custom integration to integrate daybetter_led_strip with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/daybetter_led_strip
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.match import ADDRESS, BluetoothCallbackMatcher
from homeassistant.const import (
    CONF_ADDRESS,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import callback
from homeassistant.loader import async_get_loaded_integration

from custom_components.daybetter_led_strip.models import DaybetterLedStripData

from .const import DOMAIN
from .coordinator import DaybetterLedStripCoordinator

if TYPE_CHECKING:
    from homeassistant.core import Event, HomeAssistant

    from .models import DaybetterLedStripConfigEntry


_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.LIGHT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaybetterLedStripConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    address: str = entry.data[CONF_ADDRESS]

    led_strip = DaybetterLedStrip(address)

    # It's fine if the device isn't available right now
    ble_device = bluetooth.async_last_service_info(
        hass, address.upper(), connectable=True
    )

    @callback
    def _async_update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        _change: bluetooth.BluetoothChange,
    ) -> None:
        """Update from a ble callback."""
        entry.async_create_task(
            hass,
            led_strip.update_device(service_info.device, service_info.advertisement),
        )

    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            _async_update_ble,
            BluetoothCallbackMatcher({ADDRESS: address}),
            bluetooth.BluetoothScanningMode.PASSIVE,
        )
    )
    coordinator = DaybetterLedStripCoordinator(
        hass=hass, logger=_LOGGER, name=DOMAIN, config_entry=entry
    )
    entry.runtime_data = DaybetterLedStripData(
        device=led_strip,
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # Listen for changes
    entry.async_on_unload(led_strip.on_change())

    # Attach device info
    if ble_device is not None:
        led_strip.update_device(ble_device.device, ble_device.advertisement)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    @callback
    async def _async_stop(_event: Event) -> None:
        """Disconnect device."""
        await led_strip.disconnect()

    # Force disconnect when Home Assistant stops
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_stop)
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: DaybetterLedStripConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: DaybetterLedStripConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
