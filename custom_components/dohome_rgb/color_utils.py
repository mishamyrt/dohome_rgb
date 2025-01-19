"""Color utilities for DoHome RGB lights."""
from .constants import BULB_KELVIN_MAX, BULB_KELVIN_MIN

MIREDS_MIN = 166
MIREDS_MAX = 400

KELVIN_DELTA = BULB_KELVIN_MAX - BULB_KELVIN_MIN
MIREDS_DELTA = MIREDS_MAX - MIREDS_MIN

def kelvin_to_mired(kelvin):
    """Converts a Kelvin temperature to a mired color temperature."""
    if kelvin < BULB_KELVIN_MIN:
        return MIREDS_MAX
    if kelvin > BULB_KELVIN_MAX:
        return MIREDS_MIN
    progress = (kelvin - BULB_KELVIN_MIN) / KELVIN_DELTA
    return int(MIREDS_MIN + ((1 - progress) * MIREDS_DELTA))
