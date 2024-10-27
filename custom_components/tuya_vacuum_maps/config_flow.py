"""Support Home Assistant config flow to create a config entry."""

from homeassistant import config_entries
from .const import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Vacuum Maps."""

    # The schema version of the entries that it creates
    # Home Asssistant will call the migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, info) -> None:
        """
        Invoked when a user initiates a flow via the user interface,
        or when discovered and the matching step is not defined.
        """
