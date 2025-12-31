"""Options flow for the Daybetter LED Strip integration."""

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlowResult, OptionsFlowWithReload

from custom_components.daybetter_led.const import CONF_COLOR_CORRECTION

OPTIONS_SCHEMA = vol.Schema({vol.Optional(CONF_COLOR_CORRECTION, default=True): bool})


class DaybetterLedStripOptionsFlow(OptionsFlowWithReload):
    """Runtime configuration flow for color correction."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )
