"""Handle Home Assistant config flow for the Tuya Vacuum Maps integration."""

from typing import Any, override

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICE_ID,
    CONF_NAME,
)

from .const import CONF_SERVER, CONF_SERVER_WEST_AMERICA, CONF_SERVERS, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Vacuum Maps."""

    # Schema version of the entries it creates
    # Home Assistant will call the migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Invoked when a user initiates a flow via the user interface.
        Also called when discovered but a matching discovery step is not defined.
        """

        if user_input is not None:
            # Process the information
            return self.async_create_entry(
                title=user_input.pop(CONF_NAME), data=user_input
            )

        # Define the schema of the form
        data_schema = vol.Schema(
            {
                # Device Name
                vol.Required(CONF_NAME, default="Vacuum Map"): str,
                # Server API URL
                vol.Required(CONF_SERVER, default=CONF_SERVER_WEST_AMERICA): vol.In(
                    CONF_SERVERS
                ),
                # Client ID
                vol.Required(CONF_CLIENT_ID, default=""): str,
                # Client Secret
                vol.Required(CONF_CLIENT_SECRET, default=""): str,
                # Device ID
                vol.Required(CONF_DEVICE_ID, default=""): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema)
