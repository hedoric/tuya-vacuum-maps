"""Script to parse data from a vacuum map."""

import logging

from custom_components.tuya_vacuum_maps.vacuum_map import VacuumMap

from custom_components.tuya_vacuum_maps.vacuum_path import VacuumPath
from PIL import Image
import smartcrop

logging.basicConfig(level=logging.DEBUG)


def main():
    """Parse data from a vacuum map."""

    with open("path.bin", "rb") as path_file:
        with open("layout.bin", "rb") as file:
            # Read the file as a hex string
            layout_data = file.read().hex()

            vacuum_map = VacuumMap(layout_data)

            print(vars(vacuum_map.header))
            layout_image = vacuum_map.to_image()

            # layout_image.save("layout.png")
            layout_image = layout_image.resize(
                (layout_image.width * 8, layout_image.height * 8),
                resample=Image.Resampling.NEAREST,
            )

            path_data = path_file.read().hex()
            vacuum_path = VacuumPath(path_data)
            path_image = vacuum_path.to_image(
                vacuum_map.header.origin_x, vacuum_map.header.origin_y
            )
            # path_image.save("path.png")

            layout_image.paste(path_image, (0, 0), mask=path_image)

            # Allow the origin to be moved (by offset)

            height = 8 * 430
            width = 8 * 300

            offset_x = 50
            offset_y = 50

            origin_x = (vacuum_map.header.origin_x + offset_x) * 8
            origin_y = (vacuum_map.header.origin_y + offset_y) * 8

            layout_image = layout_image.crop(
                (
                    origin_x - width / 2,
                    origin_y - height / 2,
                    origin_x + width / 2,
                    origin_y + height / 2,
                )
            )
            layout_image.save("combined.png")


if __name__ == "__main__":
    main()
