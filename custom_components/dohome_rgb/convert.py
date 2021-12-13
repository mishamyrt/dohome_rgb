"""Converters for DoHome number format."""
from __future__ import annotations

def _dohome_percent(value: int) -> int:
    """Convert dohome value (0-5000) to percent (0-1)."""
    return int(value / 5000)

def _dohome_to_uint8(value: int) -> int:
    """Convert dohome value (0-5000) to uint8 (0-255)."""
    return int(255 * _dohome_percent(value))

def _uint8_to_dohome(value: int) -> int:
    return int(5000 * (value / 255))
