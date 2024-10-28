"""Vacuum Map camera entity integration for Home Assistant."""

import logging

from typing import override
from enum import Enum
import requests
import io

from custom_components.tuya_vacuum_maps.tuya import TuyaCloudAPI
from custom_components.tuya_vacuum_maps.vacuum_map import VacuumMap
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
    server = config.data["server"]
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
            )
        ]
    )


class VacuumMapCamera(Camera):
    """Vacuum Map camera entity."""

    def __init__(
        self, entity_id: str, client_id: str, client_secret: str, device_id: str
    ) -> None:
        """Initialize the camera entity."""
        _LOGGER.debug("Initializing new VacuumMapCamera")
        self._client_id = client_id
        self._client_secret = client_secret
        self._device_id = device_id
        self._status = CameraStatus.INITIALIZING
        self._image = None
        super().__init__()

    def update(self) -> None:
        """Fetch the latest data."""

        # Request the realtime layout and path from the Tuya Cloud API
        _LOGGER.debug("Fetching realtime map")
        tuya = TuyaCloudAPI(
            base=BASE, client_id=self._client_id, client_secret=self._client_secret
        )
        endpoint = f"/v1.0/users/sweepers/file/{self._device_id}/realtime-map"
        response = tuya.request(endpoint)
        _LOGGER.debug(response)

        # Get layout and path file URLs
        layout_url = response["result"][0]["map_url"]
        path_url = response["result"][1]["map_url"]

        # Download the layout and path files
        layout_data = requests.get(layout_url, timeout=2.5).content.hex()
        path_data = requests.get(path_url, timeout=2.5).content.hex()

        # Parse the layout and path files
        vacuum_map = VacuumMap(layout_data, path_data)

        # Crop the image
        image = vacuum_map.to_image()
        cropped_image = VacuumMap.crop_image(
            image,
            410,
            250,
            vacuum_map.layout.origin_x,
            vacuum_map.layout.origin_y,
            offset_x=50,
            offset_y=60,
        )

        # Convert the image to bytes
        img_byte_arr = io.BytesIO()
        cropped_image.save(img_byte_arr, format="PNG")
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
