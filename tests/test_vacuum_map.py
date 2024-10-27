"""Test the vacuum_map module."""

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
        assert vacuum_map.header.origin_x == 300.0
        assert vacuum_map.header.origin_y == 300.0
        assert vacuum_map.header.map_resolution == 0
        assert vacuum_map.header.pile_x == 302.0
        assert vacuum_map.header.pile_y == 300.0
        assert vacuum_map.header.length_after_compression == 27666
        assert not vacuum_map.header.room_editable


def test_vacuum_map_room():
    """Test how a vacuum map room is parsed."""

    with open("./tests/layout.bin", "rb") as file:
        # Read the file as a hex string
        data = file.read().hex()

        # Parse the map data
        vacuum_map = VacuumMap(data)

        # Assert that the room values are correct
        assert vacuum_map.rooms[0].id == 5
        assert vacuum_map.rooms[0].order == 65535
        assert vacuum_map.rooms[0].sweep_count == 1
        assert vacuum_map.rooms[0].mop_count == 2
        assert vacuum_map.rooms[0].color_order == 0
        assert vacuum_map.rooms[0].sweep_forbidden == 0
        assert vacuum_map.rooms[0].mop_forbidden == 0
        assert vacuum_map.rooms[0].fan == 2
        assert vacuum_map.rooms[0].water_level == 3
        assert vacuum_map.rooms[0].y_mode == 1
        assert vacuum_map.rooms[0].name_length == 0
        assert vacuum_map.rooms[0].name == ""
        assert vacuum_map.rooms[0].vertex_num == 0
        assert vacuum_map.rooms[0].vertex_str == ""
