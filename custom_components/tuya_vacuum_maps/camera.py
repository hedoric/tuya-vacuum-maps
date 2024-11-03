"""Vacuum Map camera entity integration for Home Assistant."""

import logging

from typing import override
from enum import Enum
import io

from tuya_vacuum import TuyaVacuum

# from custom_components.tuya_vacuum_maps.tuya import TuyaCloudAPI
# from custom_components.tuya_vacuum_maps.vacuum_map import VacuumMap
from homeassistant.components.camera import (
    Camera,
    ENTITY_ID_FORMAT,
    CameraEntityFeature,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

_LOGGER = logging.getLogger(__name__)

BASE = "https://openapi.tuyaus.com"


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entries, discovery_info=None
) -> bool:
    _LOGGER.debug("Setting up VacuumMapCamera")
    name = config.title
    entity_id = generate_entity_id(ENTITY_ID_FORMAT, name, hass=hass)
    origin = config.data["server"]
    client_id = config.data["client_id"]
    secret_key = config.data["client_secret"]
    device_id = config.data["device_id"]

    _LOGGER.debug("Adding entities")
    async_add_entries(
        [
            VacuumMapCamera(
                entity_id,
                client_id,
                secret_key,
                device_id,
                origin,
            )
        ]
    )


class VacuumMapCamera(Camera):
    """Vacuum Map camera entity."""

    def __init__(
        self,
        entity_id: str,
        client_id: str,
        client_secret: str,
        device_id: str,
        origin: str,
    ) -> None:
        """Initialize the camera entity."""
        _LOGGER.debug("Initializing new VacuumMapCamera")
        self._client_id = client_id
        self._client_secret = client_secret
        self._device_id = device_id
        self._status = CameraStatus.INITIALIZING
        self._image = None
        self._origin = origin
        super().__init__()

    def update(self) -> None:
        """Fetch the latest data."""

        # Request the realtime layout and path from the Tuya Cloud API
        _LOGGER.debug("Fetching realtime map")
        vacuum = TuyaVacuum(
            origin=BASE,
            client_id=self._client_id,
            client_secret=self._client_secret,
            device_id=self._device_id,
        )

        # Fetch the realtime map
        vacuum_map = vacuum.fetch_realtime_map()

        # Get the image
        image = vacuum_map.to_image()

        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        self._image = img_byte_arr.getvalue()

    @override
    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of the camera image."""
        if self._image:
            return self._image
        else:
            return None

    async def async_added_to_hass(self) -> None:
        self.async_schedule_update_ha_state(True)

    @property
    def supported_features(self) -> int:
        return CameraEntityFeature.ON_OFF

    @property
    def should_poll(self) -> bool:
        if self._status in [CameraStatus.OK, CameraStatus.INITIALIZING]:
            return True
        else:
            return False

    @property
    def state(self) -> str:
        _LOGGER.debug("Fetching state")
        if self._status == CameraStatus.OK:
            return "on"
        if self._status == CameraStatus.FAILURE:
            return "error"
        if self._status == CameraStatus.OFF:
            return "off"
        if self._status == CameraStatus.INITIALIZING:
            return "initializing"
        return "unknown"

    @property
    def frame_interval(self) -> float:
        return 1

    def turn_on(self):
        self._status = CameraStatus.INITIALIZING

    def turn_off(self):
        self._status = CameraStatus.OFF
        self.async_schedule_update_ha_state(True)


class CameraStatus(Enum):
    INITIALIZING = "Initializing"
    OK = "OK"
    OFF = "OFF"
    FAILURE = "Failure"
