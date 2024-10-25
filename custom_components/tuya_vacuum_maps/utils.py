from typing import Iterable


def chunks(lst: Iterable, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def hex_to_ints(hex_digits: str) -> list[int]:
    """Convert a hexadecimal string to a list of integers.

    Algorithm:
        1. Split the hex_digits into a list of two-character strings.
        2. Convert each two-character string from hex to an integer.
        3. Return the list of integers.

    Example:
        hex_digits = "4a6f686e"
        - "4a" -> 74
        - "6f" -> 111
        - "68" -> 104
        - "6e" -> 110
        Output: [74, 111, 104, 110]
    """
    return [int(hex_digits[i : i + 2], 16) for i in range(0, len(hex_digits), 2)]


def combine_high_low_to_int(high: int, low: int) -> int:
    """Combine two bytes into a single integer.

    This function combines two bytes (high and low) into a single integer.
    It does this by shifting the high byte 8 bits to the left and then adding the low byte.

    Example:
        high = `0x12` (18 in decimal)
        low = `0x34` (52 in decimal)
        1. Shift 'high' 8 bits to the left.
            `0x12 << 8 = 0x1200 (4608 in decimal)`
        2. Add 'low' to the result of the shift operation.
            `0x1200 + 0x34 = 0x1234 (4660 in decimal)`

    Usage:
        This function is useful when dealing with data that is split into high and low bytes.
        For example, when parsing binary data formats.
    """
    return low + (high << 8)
