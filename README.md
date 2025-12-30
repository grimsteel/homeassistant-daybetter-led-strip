# Home Assistant Daybetter LED Strip

Home Assistant integration for Daybetter's BLE LED strips (and likely other Bluetooth-enabled Daybetter LED products).

## Installation

Available on HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=grimsteel&repository=homeassistant-daybetter-led-strip)

## Usage

The integration will autodiscover devices with the appropriate Bluetooth service. Adding the integration manually will show a list of discovered devices.

## Backend and Protocol Information

This integration uses my [`daybetter-led-strip` package](https://github.com/grimsteel/daybetter-led-strip). The README for that project includes