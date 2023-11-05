"""
Color science utilities.

Utility methods for color science constants and color space
conversions that aren't HCT or CAM16.
"""


from typing import Any
from .math_utils import clamp_int, matrix_multiply

import math
import numpy as np
from numba import njit
from numpy import ndarray, dtype


SRGB_TO_XYZ: ndarray[Any, dtype[Any]] = np.array(
    [
        [0.41233895, 0.35762064, 0.18051042],
        [0.2126, 0.7152, 0.0722],
        [0.01932141, 0.11916382, 0.95034478],
    ]
)
XYZ_TO_SRGB: ndarray[Any, dtype[Any]] = np.array(
    [
        [
            3.2413774792388685,
            -1.5376652402851851,
            -0.49885366846268053,
        ],
        [
            -0.9691452513005321,
            1.8758853451067872,
            0.04156585616912061,
        ],
        [
            0.05562093689691305,
            -0.20395524564742123,
            1.0571799111220335,
        ],
    ]
)
WHITE_POINT_D65: ndarray[Any, dtype[Any]] = np.array([95.047, 100.0, 108.883])


@njit
def rshift(val, n) -> Any:
    """
    Converts a color from RGB components to ARGB format.
    """

    return val >> n if val >= 0 else (val + 0x100000000) >> n


@njit
def argb_from_rgb(red, green, blue) -> Any:
    return rshift((255 << 24 | (red & 255) << 16 | (green & 255) << 8 | blue & 255), 0)


@njit
def alpha_from_argb(argb) -> Any:
    """
    Returns the alpha component of a color in ARGB format.
    """

    return argb >> 24 & 255


@njit
def red_from_argb(argb) -> Any:
    """
    Returns the red component of a color in ARGB format.
    """

    return argb >> 16 & 255


@njit
def green_from_argb(argb) -> Any:
    """
    Returns the green component of a color in ARGB format.
    """

    return argb >> 8 & 255


@njit
def blue_from_argb(argb) -> Any:
    """
    Returns the blue component of a color in ARGB format.
    """

    return argb & 255


@njit
def is_opaque(argb) -> Any:
    """
    Returns whether a color in ARGB format is opaque.
    """

    return alpha_from_argb(argb) >= 255


@njit
def argb_from_xyz(x, y, z) -> Any:
    """
    Converts a color from ARGB to XYZ.
    """

    matrix = XYZ_TO_SRGB
    linearr = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z
    linearg = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z
    linearb = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z
    r = delinearized(linearr)
    g = delinearized(linearg)
    b = delinearized(linearb)
    return argb_from_rgb(r, g, b)


@njit
def xyz_from_argb(argb):
    """
    Converts a color from XYZ to ARGB.
    """

    r = linearized(red_from_argb(argb))
    g = linearized(green_from_argb(argb))
    b = linearized(blue_from_argb(argb))
    return matrix_multiply([r, g, b], SRGB_TO_XYZ)


@njit
def lab_invf(ft):
    """
    Converts a color represented in Lab color space into an ARGB integer.
    """

    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    ft3 = ft * ft * ft
    return ft3 if ft3 > e else (116 * ft - 16) / kappa


@njit
def argd_from_lab(l, a, b):
    """
    Converts LAB color values to ARGB color value.

    Args:
        l (float): The lightness value of the LAB color.
        a (float): The green-red value of the LAB color.
        b (float): The blue-yellow value of the LAB color.

    Returns:
        int: The ARGB color value.

    """

    white_point = WHITE_POINT_D65
    fy = (l + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    xnormalized = lab_invf(fx)
    ynormalized = lab_invf(fy)
    znormalized = lab_invf(fz)
    x = xnormalized * white_point[0]
    y = ynormalized * white_point[1]
    z = znormalized * white_point[2]
    return argb_from_xyz(x, y, z)


@njit
def labf(t) -> Any:
    """
    Calculate the lightness adjustment factor for a given value.
    """

    e: float = 216.0 / 24389.0
    kappa: float = 24389.0 / 27.0

    return np.where(t > e, np.power(t, 1.0 / 3.0), (kappa * t + 16) / 116)


@njit
def lab_from_argb(argb):
    """
    Converts ARGB color value to LAB color values.
    """

    linearr_gb = np.array([linearized(red_from_argb(argb)), 
                          linearized(green_from_argb(argb)), 
                          linearized(blue_from_argb(argb))])
    matrix = np.array(SRGB_TO_XYZ)
    xyz = np.dot(matrix, linearr_gb)
    white_point = np.array(WHITE_POINT_D65)
    normalized_xyz = xyz / white_point
    fxyz = labf(normalized_xyz)
    l = 116.0 * fxyz[1] - 16
    a = 500.0 * (fxyz[0] - fxyz[1])
    b = 200.0 * (fxyz[1] - fxyz[2])
    return [l, a, b]


@njit
def argb_From_lstar(lstar):
    fy = (lstar + 16.0) / 116.0
    fz = fy
    fx = fy

    kappa = 24389.0 / 27.0
    epsilon = 216.0 / 24389.0
    l_exceeds_epsilon_kappa = lstar > 8.0

    y = fy * fy * fy if l_exceeds_epsilon_kappa else lstar / kappa

    cube_exceed_epsilon = fy * fy * fy > epsilon

    x = fx * fx * fx if cube_exceed_epsilon else lstar / kappa
    z = fz * fz * fz if cube_exceed_epsilon else lstar / kappa

    white_point = WHITE_POINT_D65

    return argb_from_xyz(x * white_point[0], y * white_point[1], z * white_point[2])


@njit
def lstar_from_argb(argb):
    y = xyz_from_argb(argb)[1] / 100.0
    e = 216.0 / 24389.0

    if y <= e:
        return 24389.0 / 27.0 * y

    y_intermediate = math.pow(y, 1.0 / 3.0)
    return 116.0 * y_intermediate - 16.0


@njit
def y_from_lstar(lstar):
    if lstar > 8:
        return math.pow((lstar + 16.0) / 116.0, 3.0) * 100.0

    return lstar / (24389.0 / 27.0) * 100.0


@njit
def linearized(rgbComponent):
    normalized = rgbComponent / 255.0

    if normalized <= 0.040449936:
        return normalized / 12.92 * 100.0

    return np.power((normalized + 0.055) / 1.055, 2.4) * 100.0


@njit
def delinearized(rgbComponent):
    normalized = rgbComponent / 100.0
    delinearized = 0.0

    if normalized <= 0.0031308:
        delinearized = normalized * 12.92

    else:
        delinearized = 1.055 * math.pow(normalized, 1.0 / 2.4) - 0.055

    return clamp_int(0, 255, round(delinearized * 255.0))


@njit
def white_point_d65() -> ndarray[Any, dtype[Any]]:
    """
    Returns the white point D65.

    Returns:
        The white point D65 as a numpy ndarray.
    """

    return WHITE_POINT_D65
