"""Handles individual Tuya vacuum devices."""


class TuyaCloudVacuum:
    """Handles a single Tuya based vacuum."""

    def __init__(self, device_id: str) -> None:
        self.device_id = device_id
