"""Handle Home Assistant config flow for the Tuya Vacuum Maps integration."""

import logging
from typing import Any, override

import voluptuous as vol

import tuya_vacuum
from tuya_vacuum.tuya import (
    CrossRegionAccessError,
    InvalidClientIDError,
    InvalidClientSecretError,
    InvalidDeviceIDError,
)

from homeassistant import config_entries
from homeassistant.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_DEVICE_ID,
    CONF_NAME,
)

from .const import CONF_SERVER, CONF_SERVER_WEST_AMERICA, CONF_SERVERS, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(data: dict) -> None:
    """Validate that the user input allows us to connect to the Tuya API."""
    _LOGGER.debug("Validating input for Tuya Vacuum Maps integration...")

    # Use your forked class Vacuum (not TuyaVacuum)
    vacuum = tuya_vacuum.Vacuum(
        data["server"],
        data["client_id"],
        data["client_secret"],
        data["device_id"],
    )

    # Will try realtime; if empty, falls back to file map (MS1)
    vacuum.fetch_map()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Vacuum Maps."""

    VERSION = 1
    MINOR_VERSION = 1

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Invoked when a user starts the setup via the UI."""

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                return self.async_create_entry(
                    title=user_input.pop(CONF_NAME), data=user_input
                )
            except CrossRegionAccessError:
                errors[CONF_SERVER] = (
                    "Cross-region access is not allowed. Check data center."
                )
            except InvalidClientIDError:
                errors[CONF_CLIENT_ID] = "Invalid Client ID."
            except InvalidClientSecretError:
                errors[CONF_CLIENT_SECRET] = "Invalid Client Secret."
            except InvalidDeviceIDError:
                errors[CONF_DEVICE_ID] = "Invalid Device ID."
            except Exception as err:  # keep broad except for unknown API errors
                _LOGGER.error("Unexpected validation error: %s", err)
                errors["base"] = "Unknown error occurred."

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="Vacuum Map"): str,
                vol.Required(CONF_SERVER, default=CONF_SERVER_WEST_AMERICA): vol.In(
                    CONF_SERVERS
                ),
                vol.Required(CONF_CLIENT_ID, default=""): str,
                vol.Required(CONF_CLIENT_SECRET, default=""): str,
                vol.Required(CONF_DEVICE_ID, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
