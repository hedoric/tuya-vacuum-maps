"""Handles individual Tuya vacuum devices."""

import


class TuyaCloudVacuum(Camera):
    """Handles a single Tuya based vacuum."""

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id

    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
