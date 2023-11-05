from ..quantize.quantizer_celebi import QuantizerCelebi
from ..score.score import Score
from .color_utils import argb_from_rgb

import numpy as np
from numba import njit
from PIL import Image


@njit
def SourceColorFromImage(image):
    """
    Get the source color from an image.

    Args:
        image: The image element from which to extract the source color.

    Returns:
        The source color, which is the color most suitable for creating a UI theme.
    """

    if (image.mode != 'RGBA'):
        print("Warning: Image not in RGB|RGBA format - Converting...")
        image = image.convert('RGBA')

    pixels = []
    np_image = np.array(image)

    for pixel in np_image.reshape(-1, 4):
        r, g, b, a = pixel

        if (a < 255):
            continue
        
        argb = argb_from_rgb(r, g, b)
        pixels.append(argb)

    result = QuantizerCelebi.quantize(pixels, 128)
    ranked = Score.score(result)
    return ranked[0]
