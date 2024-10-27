"""Classes to handle a vacuum path."""

import lz4.block
from PIL import Image, ImageDraw
from functools import reduce

from custom_components.tuya_vacuum_maps.utils import (
    create_format_path,
    deal_pl,
    hex_to_ints,
    chunks,
    combine_high_low_to_int,
)

format_path_point = create_format_path(reverse_y=True, hide_path=True)

# Large parts of this script are based on the following code:
# https://github.com/tuya/tuya-panel-demo/blob/main/examples/laserSweepRobot/src/protocol/path/index.ts

# Length of path header in bytes
PATH_HEADER_LENGTH = 26


class VacuumPathHeader:
    """Handle the header of a vacuum path."""

    def __init__(self, data: str) -> None:
        """Parse the header of a vacuum path.

        @param data: The data of the path header.
        """

        data_array = hex_to_ints(data)
        self.version = data_array[0]
        self.force_update = data_array[3]
        self.type = data_array[4]

        # This might be missing proper formatDataHeaderException handling
        self.id = [
            combine_high_low_to_int(integer[0], integer[1])
            for integer in chunks(data_array[1:3], 2)
        ][0]

        self.total_count = int(data[10:18], 16)

        # This might be missing proper formatDataHeaderException handling
        [self.theta, self.length_after_compression] = [
            combine_high_low_to_int(integer[0], integer[1])
            for integer in chunks(data_array[9:13], 2)
        ]


class VacuumPath:
    """Handle the data of a entire vacuum path."""

    def __init__(self, data: str) -> None:
        """Parse the data of a vacuum path.

        @param data: Hexadecimal string of the vacuum path.
        """

        self.header = VacuumPathHeader(data[:PATH_HEADER_LENGTH])
        print(vars(self.header))

        data_array = hex_to_ints(data)

        if self.header.length_after_compression:
            max_buffer_length = self.header.total_count * 4
            encoded_data_array = bytes(hex_to_ints(data[PATH_HEADER_LENGTH:]))
            decoded_data_array = lz4.block.decompress(
                encoded_data_array,
                uncompressed_size=max_buffer_length,
                return_bytearray=True,
            )
            path_data_array = chunks(decoded_data_array, 4)
        else:
            # Floor division
            header_length = PATH_HEADER_LENGTH // 2
            path_data_array = chunks(data_array[header_length:], 4)

        # This code is not accurate to what's expected to happen
        path_data = []
        for point in path_data_array:
            [x, y] = [
                deal_pl(combine_high_low_to_int(high, low))
                for high, low in chunks(point, 2)
            ]
            real_point = format_path_point(x, y)
            path_data.append(real_point)

        self._path_data = path_data
        self.start_count = len(path_data)
        self.current_count = len(path_data)
        self.is_full = True
        self.origin_data = data_array[:PATH_HEADER_LENGTH]

    def to_image(self, origin_x: int, origin_y: int) -> Image.Image:
        """Convert the path to an image."""

        coordinates = []
        for point in self._path_data:
            # coordinates.append(point["x"] + origin_x)
            # coordinates.append(point["y"] + origin_y)
            x = (point["x"] + origin_x) * 8
            y = (point["y"] + origin_y) * 8
            coordinates.append(x)
            coordinates.append(y)

        image = Image.new(mode="RGBA", size=(601 * 8, 601 * 8), color=(255, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # draw.line(coordinates, fill="red", width=2, joint="curve")
        draw.line(coordinates, fill="white", width=8, joint="curve")

        # This is a hacky solution to draw the charger and vacuum position
        # Not sure how else to do this yet
        draw.circle((origin_x * 8, origin_y * 8), 20, fill="white")
        draw.circle((origin_x * 8, origin_y * 8), 16, fill="green")
        if len(coordinates) >= 2:
            draw.circle((coordinates[-2], coordinates[-1]), 20, fill="white")
            draw.circle((coordinates[-2], coordinates[-1]), 16, fill="blue")

        return image
