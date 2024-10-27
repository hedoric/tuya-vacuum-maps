"""Classes to handle a vacuum map."""

# Large parts of this script are based on the following code:
# https://github.com/tuya/tuya-panel-demo/blob/main/examples/laserSweepRobot/src/protocol/map/index.ts

import logging

import lz4.block
import numpy as np
from PIL import Image, ImageColor
import re

from custom_components.tuya_vacuum_maps.const import (
    ORIGIN_MAP_COLOR,
    MAP_COLOR,
    BITMAP_TYPE_HEX_MAP,
    default_colors,
    pixel_types,
)
from custom_components.tuya_vacuum_maps.utils import (
    chunks,
    combine_high_low_to_int,
    hex_to_ints,
    shrink_number,
    create_house_color_map,
    hex_to_alpha_hex,
)

# Length of map header in bytes
MAP_HEADER_LENGTH = 48

# Max id number
MAX_ID = 255

INFO_BYTE_LEN = 26  # "Room properties"
NAME_BYTE_LEN = 20  # "Vertices_name"

_LOGGER = logging.getLogger(__name__)

HOUSE_COLOR_MAP = create_house_color_map(
    1,
    MAX_ID,
    ORIGIN_MAP_COLOR,
    MAP_COLOR["room_60_color"],
    MAP_COLOR["room_61_color"],
    MAP_COLOR["room_62_color"],
    MAP_COLOR["room_63_color"],
)


class VacuumMapHeader:
    """Handle the header of a vacuum map."""

    def __init__(self, data: str) -> None:
        """Parse the header of a vacuum map.

        @param data: The data of the map header.
        """

        # The version of the map (0: compressed, 1: uncompressed)
        self.version = int(data[0:2], 16)

        # Get the id of the map
        [self.id] = [
            combine_high_low_to_int(integer[0], integer[1])
            for integer in chunks(hex_to_ints(data[2:6]), 2)
        ]

        self.type = int(data[6:8], 16)  # The type of the map (0: layout, 1: path)
        self.total_count = int(data[36:44], 16)

        # Parse the rest of the data. Code taken from the Tuya Panel Demo
        [
            _,
            _,
            self.width,
            self.height,
            self.origin_x,
            self.origin_y,
            self.map_resolution,
            self.pile_x,
            self.pile_y,
            _,
            _,
            self.length_after_compression,
        ] = [
            combine_high_low_to_int(integer[0], integer[1])
            for integer in chunks(hex_to_ints(data), 2)
        ]

        self.origin_x = shrink_number(self.origin_x)
        self.origin_y = shrink_number(self.origin_y)
        self.pile_x = shrink_number(self.pile_x)
        self.pile_y = shrink_number(self.pile_y)

        self.room_editable = bool(self.type)


class VacuumMapRoom:
    """Handle the data of a room in the vacuum map."""

    def __init__(self, data: str, byte_pos: int) -> None:
        """Parse the data of a room in the vacuum map.

        @param data: The `map_room_array`.
        @param byte_pos: The byte position of the room in the `map_room_array`.
        """

        # "room information" according to google translate
        room_info_str = data[
            byte_pos : (byte_pos + (INFO_BYTE_LEN + NAME_BYTE_LEN + 1) * 2)
        ]

        [self.id, self.order, self.sweep_count, self.mop_count] = [
            combine_high_low_to_int(integer[0], integer[1])
            for integer in chunks(hex_to_ints(room_info_str[:16]), 2)
        ]

        [
            self.color_order,
            self.sweep_forbidden,
            self.mop_forbidden,
            self.fan,
            self.water_level,
            self.y_mode,
        ] = hex_to_ints(room_info_str[16:28])

        self.name_length = int(room_info_str[52:54], 16)
        vertices_name_str = room_info_str[
            (INFO_BYTE_LEN * 2 + 1 * 2) : (
                INFO_BYTE_LEN * 2 + 1 * 2 + self.name_length * 2
            )
        ]

        self.name = bytes.fromhex(vertices_name_str).decode()

        self.vertex_num = int(room_info_str[-2:], 16)
        self.vertex_str = data[
            (byte_pos + (INFO_BYTE_LEN + NAME_BYTE_LEN + 1) * 2) : (
                byte_pos
                + (INFO_BYTE_LEN + NAME_BYTE_LEN + 1) * 2
                + self.vertex_num * 2 * 2 * 2
            )
        ]

    @staticmethod
    def parse_map_room_array(data: str) -> list["VacuumMapRoom"]:
        """Parse the map room array.

        @param data: The `map_room_array`.
        """

        rooms = []
        room_count = int(data[2:4], 16)

        byte_pos = 2 * 2  # "region_num"

        for _ in range(room_count):
            rooms.append(VacuumMapRoom(data, byte_pos))
            byte_pos = byte_pos + (INFO_BYTE_LEN + NAME_BYTE_LEN + 1) * 2

        return rooms


class VacuumMap:
    """Handle the data of a entire vacuum map."""

    def __init__(self, data: str) -> None:
        """Parse the data of a vacuum map.

        @param data: Hexadecimal string of the vacuum map.
        """

        # Parse the header of the map
        # Should the variables in the header be available without needing to access the header?
        self.header = VacuumMapHeader(data[:MAP_HEADER_LENGTH])

        # Invalid map type
        if self.header.type > 255:
            raise RuntimeError(f"Map header type: {self.header.type} is not valid.")

        print(vars(self.header))

        # Parse the rest of the map data
        match self.header.version:
            case 0:
                self._parse_map_version_0(data)

            case 1:
                self._parse_map_version_1(data)

            case 2:
                self._parse_map_version_2(data)

            # Default case
            case _:
                raise NotImplementedError(
                    f"Map version {self.header.version} is not supported."
                )

    def to_image(self) -> Image.Image:
        """Convert the map to an image.

        Taken from tuya_cloud_map_extractor.
        """
        pixels = []
        colors = {
            # "bg_color": default_colors.v1.get("bg_color"),
            "bg_color": ImageColor.getcolor("#006ee6", "RGB"),
            # "wall_color": default_colors.v1.get("wall_color"),
            "wall_color": ["50", "50", "50"],
            # "fun_color": default_colors.v1.get("room_color"),
            "fun_color": ["150", "150", "150"],
        }
        for index, room in enumerate(self.rooms):
            # This is terrible
            colors["room_color_" + str(room.id)] = ImageColor.getcolor(
                ORIGIN_MAP_COLOR[index], "RGB"
            )

        for height_counter in range(self.header.height):
            line = []
            for width_counter in range(self.header.width):
                pixel_type = pixel_types.v1.get(
                    self._map_data_array[
                        width_counter + height_counter * self.header.width
                    ]
                )
                pixel = colors.get(pixel_type)
                if not pixel:
                    print(f"Unknown pixel type: {pixel_type}")
                    pixel = (20, 20, 20)
                line.append(pixel)
            pixels.append(line)
        return Image.fromarray(np.array(pixels, dtype=np.uint8))

    def _parse_map_version_0(self, data: str):
        """Parse the data of a vacuum map with version 0."""
        # "Normal Version" according to google translate
        # raise NotImplementedError("Map version 0 is not yet supported.")
        # If the data is compressed, decompress it
        if self.header.length_after_compression:
            max_buffer_length = self.header.total_count * 8
            encoded_data_array = bytes(hex_to_ints(data[MAP_HEADER_LENGTH:]))
            decoded_data_array = lz4.block.decompress(
                encoded_data_array,
                uncompressed_size=max_buffer_length,
                return_bytearray=True,
            )
            area = self.header.width * self.header.height

            mapDataStr = "".join(
                "".join(
                    "".join(
                        BITMAP_TYPE_HEX_MAP[x]
                        for x in re.findall(r"\w{2}", format(d, "08b"))
                    )
                )
                for d in decoded_data_array
            )[: area * 2]

            self.rooms = []
            self._map_data_array = bytes.fromhex(mapDataStr)
        else:
            raise NotImplementedError("Uncompressed map data is not yet supported.")

    def _parse_map_version_1(self, data: str):
        """Parse the data of a vacuum map with version 1."""
        # "Partition Version" according to google translate

        # If the data is compressed, decompress it
        if self.header.length_after_compression:
            area = self.header.width * self.header.height
            info_length = MAP_HEADER_LENGTH + self.header.total_count * 2
            encoded_data_array = bytes(hex_to_ints(data[MAP_HEADER_LENGTH:info_length]))
            max_buffer_length = self.header.total_count * 4
            decoded_data_array = lz4.block.decompress(
                encoded_data_array,
                uncompressed_size=max_buffer_length,
                return_bytearray=True,
            )

            self._map_data_array = decoded_data_array[:area]
            map_room_array = decoded_data_array[area:]

            rooms = VacuumMapRoom.parse_map_room_array(map_room_array.hex())

            for room in rooms:
                _LOGGER.debug(vars(room))

            self.rooms = rooms

        else:
            raise NotImplementedError("Uncompressed map data is not yet supported.")

    def _parse_map_version_2(self, data: str):
        """Parse the data of a vacuum map with version 2."""
        # "Floor Material Version" according to google translate
        raise NotImplementedError("Map version 2 is not yet supported.")
