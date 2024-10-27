"""Tests for custom_components.tuya_vacuum_maps.utils."""

from custom_components.tuya_vacuum_maps.utils import hex_to_alpha_hex


def test_hex_to_alpha_hex():
    """Test hex_to_alpha_hex."""
    assert hex_to_alpha_hex("#000000", 0.4) == "#66000000"
