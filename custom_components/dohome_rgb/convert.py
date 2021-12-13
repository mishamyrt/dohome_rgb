def _dohome_percent(value):
    """Converts dohome value (0-5000) to percent (0-1)"""
    return value / 5000

def _dohome_to_uint8(value):
    """Converts dohome value (0-5000) to uint8 (0-255)"""
    return 255 * _dohome_percent(value)
