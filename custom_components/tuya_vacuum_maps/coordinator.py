"""Handle API polling and data retrieval."""

import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class TuyaCloudVacuumMapsCoordinator(DataUpdateCoordinator):
    """Handle API polling and data retrieval."""

    def __init__(self, hass, api):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data, for logging purposes
            name="Tuya Cloud API",
            # Set always_update to false if the data returned
            # by the API can be compared to avoid duplicate updates
            always_update=True,
        )
        self.api = api

        super().__init__(
            hass,
            _LOGGER,
            name="Tuya Cloud Vacuum Maps",
            update_interval=interval,
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        return await self.api.async_get_map_data(self.device_id)
