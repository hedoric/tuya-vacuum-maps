"""Functional test for communication with the Tuya Cloud API."""

import os

from custom_components.tuya_vacuum_maps.tuya import tuya_request

from dotenv import load_dotenv


def test_tuya_request_token():
    """Functionally test the tuya_request."""

    # Load environment variables
    load_dotenv()

    # Get environment variables
    CLIENT_ID = os.environ["CLIENT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]

    BASE = "https://openapi.tuyaeu.com"
    ENDPOINT = "/v1.0/token?grant_type=1"
    response = tuya_request(BASE, ENDPOINT, CLIENT_ID, CLIENT_SECRET)
    print(response)
    assert response["success"]
