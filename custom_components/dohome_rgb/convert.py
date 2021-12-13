def _dohome_percent(value):
    return value / 5000

def _dohome_to_uint8(value):
    return 255 * _dohome_percent(value)
