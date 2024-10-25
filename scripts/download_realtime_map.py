"""Script to download the current realtime map from a vacuum using the Tuya Cloud API."""

import os

import requests
from dotenv import load_dotenv
from custom_components.tuya_vacuum_maps.tuya import TuyaCloudAPI

# Load environment variables
load_dotenv()

# Get environment variables
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
DEVICE_ID = os.environ["DEVICE_ID"]


def main():
    """Download the current realtime map from a vacuum using the Tuya Cloud API."""

    BASE = "https://openapi.tuyaus.com"
    ENDPOINT = f"/v1.0/users/sweepers/file/{DEVICE_ID}/realtime-map"

    tuya = TuyaCloudAPI(base=BASE, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    response = tuya.request(ENDPOINT)

    maps = response["result"]
    print(maps)

    for vacuum_map in maps:
        if vacuum_map["map_type"] == 0:
            # Layout Map, Download this
            map_url = vacuum_map["map_url"]
            map_data = requests.get(map_url, timeout=2.5).content

            # Save Map Data
            with open("layout.bin", "wb") as file:
                file.write(map_data)
        else:
            # Unknown Map Type
            print(f"Unknown Map Type: {vacuum_map['map_type']}")


if __name__ == "__main__":
    main()
