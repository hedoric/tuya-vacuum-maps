"""Functional test for communication with the Tuya Cloud API."""

import os

from custom_components.tuya_vacuum_maps.tuya import TuyaCloudAPI

from dotenv import load_dotenv


def test_tuya_request():
    """Functionally test the tuya_request."""

    # Load environment variables
    load_dotenv()

    # Get environment variables
    CLIENT_ID = os.environ["CLIENT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    DEVICE_ID = os.environ["DEVICE_ID"]

    BASE = "https://openapi.tuyaus.com"
    ENDPOINT = f"/v1.0/users/sweepers/file/{DEVICE_ID}/realtime-map"
    tuya = TuyaCloudAPI(base=BASE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    response = tuya.request(ENDPOINT)
    print(response)
    assert response["success"]
