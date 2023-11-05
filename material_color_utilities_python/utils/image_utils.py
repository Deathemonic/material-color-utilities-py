from ..quantize.quantizer_celebi import *
from ..score.score import *
from .color_utils import *

import numpy as np
from numba import njit


@njit
def sourceColorFromImage(image):
    """
    Get the source color from an image.

    param: image The image element
    Return: Source color - the color most suitable for creating a UI theme
    """

    if image.mode == "RGB":
        image = image.convert("RGBA")
    if image.mode != "RGBA":
        print("Warning: Image not in RGB|RGBA format - Converting...")
        image = image.convert("RGBA")

    # Convert image to NumPy array
    data = np.array(image)

    # Extract RGB values
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # Filter out pixels with alpha < 255
    mask = a == 255

    # Apply mask to RGB values
    r, g, b = r[mask], g[mask], b[mask]

    # Convert RGB to ARGB
    pixels = np.array([argbFromRgb(ri, gi, bi) for ri, gi, bi in zip(r, g, b)])

    result = QuantizerCelebi.quantize(pixels, 128)
    ranked = Score.score(result)
    top = ranked[0]
    return top
