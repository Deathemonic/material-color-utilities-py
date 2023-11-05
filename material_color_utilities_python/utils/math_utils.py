"""
Utility methods for mathematical operations.
"""

import numpy as np
from numba import njit


@njit
def signum(num):
    """
    The signum function.

    Return:
    1 if num > 0, -1 if num < 0, and 0 if num = 0
    """

    if num < 0:
        return -1
    elif num == 0:
        return 0
    else:
        return 1


@njit
def lerp(start, stop, amount):
    """
    The linear interpolation function.
    Return:
    start if amount = 0 and stop if amount = 1
    """

    return (1.0 - amount) * start + amount * stop


@njit
def clampInt(min, max, input):
    """
    Clamps an integer between two integers.

    Return input when min <= input <= max, and either min or max otherwise.
    """

    if input < min:
        return min
    elif input > max:
        return max
    return input


@njit
def clampDouble(min, max, input):
    """
    Clamps an integer between two floating-point numbers.
    Return:
    Input when min <= input <= max, and either min or max otherwise.
    """

    if input < min:
        return min
    elif input > max:
        return max
    return input


@njit
def sanitizeDegreesInt(degrees):
    """
    Sanitizes a degree measure as an integer.

    Return:
    A degree measure between 0 (inclusive) and 360
    """

    degrees = degrees % 360
    if degrees < 0:
        degrees = degrees + 360
    return degrees


@njit
def sanitizeDegreesDouble(degrees):
    """
    Sanitizes a degree measure as a floating-point number.
    Eeturn:
    A degree measure between 0.0 (inclusive) and 360.0
    """

    degrees = degrees % 360.0
    if degrees < 0:
        degrees = degrees + 360.0
    return degrees


@njit
def differenceDegrees(a, b):
    """
    Distance of two points on a circle, represented using degrees.
    """

    return 180.0 - np.abs(np.abs(a - b) - 180.0)


@njit
def matrixMultiply(row, matrix):
    """
    Multiplies a 1x3 row vector with a 3x3 matrix.
    """

    a = row[0] * matrix[0][0] + row[1] * matrix[0][1] + row[2] * matrix[0][2]
    b = row[0] * matrix[1][0] + row[1] * matrix[1][1] + row[2] * matrix[1][2]
    c = row[0] * matrix[2][0] + row[1] * matrix[2][1] + row[2] * matrix[2][2]
    return np.array([a, b, c])
