"""Script to parse data from a vacuum map."""

import logging

from custom_components.tuya_vacuum_maps.vacuum_map import VacuumMap

logging.basicConfig(level=logging.DEBUG)


def main():
    """Parse data from a vacuum map."""

    with open("layout.bin", "rb") as file:
        # Read the file as a hex string
        data = file.read().hex()

        vacuum_map = VacuumMap(data)

        print(vars(vacuum_map.header))
        image = vacuum_map.to_image()
        image.save("layout.png")


if __name__ == "__main__":
    main()
