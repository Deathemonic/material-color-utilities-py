"""
Color science utilities.

Utility methods for color science constants and color space
conversions that aren't HCT or CAM16.
"""


from typing import Any
from .math_utils import *

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
def argbFromRgb(red, green, blue) -> Any:
    return rshift((255 << 24 | (red & 255) << 16 | (green & 255) << 8 | blue & 255), 0)


@njit
def alphaFromArgb(argb) -> Any:
    """
    Returns the alpha component of a color in ARGB format.
    """

    return argb >> 24 & 255


@njit
def redFromArgb(argb) -> Any:
    """
    Returns the red component of a color in ARGB format.
    """

    return argb >> 16 & 255


@njit
def greenFromArgb(argb) -> Any:
    """
    Returns the green component of a color in ARGB format.
    """

    return argb >> 8 & 255


@njit
def blueFromArgb(argb) -> Any:
    """
    Returns the blue component of a color in ARGB format.
    """

    return argb & 255


@njit
def isOpaque(argb) -> Any:
    """
    Returns whether a color in ARGB format is opaque.
    """

    return alphaFromArgb(argb) >= 255


@njit
def argbFromXyz(x, y, z) -> Any:
    """
    Converts a color from ARGB to XYZ.
    """

    matrix = XYZ_TO_SRGB
    linearR = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z
    linearG = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z
    linearB = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z
    r = delinearized(linearR)
    g = delinearized(linearG)
    b = delinearized(linearB)
    return argbFromRgb(r, g, b)


# /**
#  * Converts a color from XYZ to ARGB.
#  */
def xyzFromArgb(argb):
    r = linearized(redFromArgb(argb))
    g = linearized(greenFromArgb(argb))
    b = linearized(blueFromArgb(argb))
    return matrixMultiply([r, g, b], SRGB_TO_XYZ)


# /**
#  * Converts a color represented in Lab color space into an ARGB
#  * integer.
#  */
def labInvf(ft):
    e = 216.0 / 24389.0
    kappa = 24389.0 / 27.0
    ft3 = ft * ft * ft
    if ft3 > e:
        return ft3
    else:
        return (116 * ft - 16) / kappa


def argbFromLab(l, a, b):
    whitePoint = WHITE_POINT_D65
    fy = (l + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0
    xNormalized = labInvf(fx)
    yNormalized = labInvf(fy)
    zNormalized = labInvf(fz)
    x = xNormalized * whitePoint[0]
    y = yNormalized * whitePoint[1]
    z = zNormalized * whitePoint[2]
    return argbFromXyz(x, y, z)


@njit
def labF(t) -> Any:
    """
    Converts a color from ARGB representation to L*a*b* representation.
    param: argb the ARGB representation of a color
    Return: a Lab object representing the color
    """

    e: float = 216.0 / 24389.0
    kappa: float = 24389.0 / 27.0

    if t > e:
        return np.power(t, 1.0 / 3.0)
    return (kappa * t + 16) / 116


def labFromArgb(argb):
    linearR = linearized(redFromArgb(argb))
    linearG = linearized(greenFromArgb(argb))
    linearB = linearized(blueFromArgb(argb))
    matrix = SRGB_TO_XYZ
    x = matrix[0][0] * linearR + matrix[0][1] * linearG + matrix[0][2] * linearB
    y = matrix[1][0] * linearR + matrix[1][1] * linearG + matrix[1][2] * linearB
    z = matrix[2][0] * linearR + matrix[2][1] * linearG + matrix[2][2] * linearB
    whitePoint = WHITE_POINT_D65
    xNormalized = x / whitePoint[0]
    yNormalized = y / whitePoint[1]
    zNormalized = z / whitePoint[2]
    fx = labF(xNormalized)
    fy = labF(yNormalized)
    fz = labF(zNormalized)
    l = 116.0 * fy - 16
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return [l, a, b]


# /**
#  * Converts an L* value to an ARGB representation.
#  *
#  * @param lstar L* in L*a*b*
#  * @return ARGB representation of grayscale color with lightness
#  * matching L*
#  */
def argbFromLstar(lstar):
    fy = (lstar + 16.0) / 116.0
    fz = fy
    fx = fy
    kappa = 24389.0 / 27.0
    epsilon = 216.0 / 24389.0
    lExceedsEpsilonKappa = lstar > 8.0
    y = fy * fy * fy if lExceedsEpsilonKappa else lstar / kappa
    cubeExceedEpsilon = fy * fy * fy > epsilon
    x = fx * fx * fx if cubeExceedEpsilon else lstar / kappa
    z = fz * fz * fz if cubeExceedEpsilon else lstar / kappa
    whitePoint = WHITE_POINT_D65
    return argbFromXyz(x * whitePoint[0], y * whitePoint[1], z * whitePoint[2])


# /**
#  * Computes the L* value of a color in ARGB representation.
#  *
#  * @param argb ARGB representation of a color
#  * @return L*, from L*a*b*, coordinate of the color
#  */
def lstarFromArgb(argb):
    y = xyzFromArgb(argb)[1] / 100.0
    e = 216.0 / 24389.0
    if y <= e:
        return 24389.0 / 27.0 * y
    else:
        yIntermediate = math.pow(y, 1.0 / 3.0)
        return 116.0 * yIntermediate - 16.0


# /**
#  * Converts an L* value to a Y value.
#  *
#  * L* in L*a*b* and Y in XYZ measure the same quantity, luminance.
#  *
#  * L* measures perceptual luminance, a linear scale. Y in XYZ
#  * measures relative luminance, a logarithmic scale.
#  *
#  * @param lstar L* in L*a*b*
#  * @return Y in XYZ
#  */
def yFromLstar(lstar):
    ke = 8.0
    if lstar > 8:
        return math.pow((lstar + 16.0) / 116.0, 3.0) * 100.0
    return lstar / (24389.0 / 27.0) * 100.0


# /**
#  * Linearizes an RGB component.
#  *
#  * @param rgbComponent 0 <= rgb_component <= 255, represents R/G/B
#  * channel
#  * @return 0.0 <= output <= 100.0, color channel converted to
#  * linear RGB space
#  */
def linearized(rgbComponent):
    normalized = rgbComponent / 255.0
    if normalized <= 0.040449936:
        return normalized / 12.92 * 100.0
    return np.power((normalized + 0.055) / 1.055, 2.4) * 100.0


# /**
#  * Delinearizes an RGB component.
#  *
#  * @param rgbComponent 0.0 <= rgb_component <= 100.0, represents
#  * linear R/G/B channel
#  * @return 0 <= output <= 255, color channel converted to regular
#  * RGB space
#  */
def delinearized(rgbComponent):
    normalized = rgbComponent / 100.0
    delinearized = 0.0
    if normalized <= 0.0031308:
        delinearized = normalized * 12.92
    else:
        delinearized = 1.055 * math.pow(normalized, 1.0 / 2.4) - 0.055
    return clampInt(0, 255, round(delinearized * 255.0))


def whitePointD65() -> ndarray[Any, dtype[Any]]:
    """
    Returns the standard white point white on a sunny day.

    Return: The white point
    """
    return WHITE_POINT_D65
