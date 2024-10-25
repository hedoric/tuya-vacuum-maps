"""Test the vacuum_map module."""

import pytest

from custom_components.tuya_vacuum_maps.vacuum_map import VacuumMap


def test_vacuum_map_header():
    """Test how the vacuum map header is parsed."""

    with open("./tests/layout.bin", "rb") as file:
        # Read the file as a hex string
        data = file.read().hex()

        # Parse the map data
        vacuum_map = VacuumMap(data)

        # Assert that the header values are correct
        assert vacuum_map.header.version == 1
        assert vacuum_map.header.id == 0
        assert vacuum_map.header.type == 0
        assert vacuum_map.header.total_count == 361391
        assert vacuum_map.header.width == 601
        assert vacuum_map.header.height == 601
        assert vacuum_map.header.origin_x == 3000
        assert vacuum_map.header.origin_y == 3000
        assert vacuum_map.header.map_resolution == 0
        assert vacuum_map.header.pile_x == 3020
        assert vacuum_map.header.pile_y == 3000
        assert vacuum_map.header.length_after_compression == 27666
        assert not vacuum_map.header.room_editable
