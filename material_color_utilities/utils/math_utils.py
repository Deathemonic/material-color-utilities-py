"""
Utility methods for mathematical operations.
"""

import numpy as np
from numba import njit


def signum(num):
    """
    Returns the sign of a number.

    Args:
        num: The number to determine the sign of.

    Returns:
        1 if num > 0, -1 if num < 0, and 0 if num = 0.
    """

    if num < 0:
        return -1
    elif num == 0:
        return 0
    return 1


@njit
def lerp(start, stop, amount):
    """
    Performs linear interpolation between two values.

    Args:
        start: The starting value.
        stop: The ending value.
        amount: The interpolation amount between 0.0 and 1.0.

    Returns:
        The interpolated value between start and stop.
    """

    return (1.0 - amount) * start + amount * stop


@njit
def clamp_int(min, max, input):
    """
    Clamps an integer value between a minimum and maximum value.

    Args:
        min (int): The minimum value to clamp to.
        max (int): The maximum value to clamp to.
        input (int): The input value to be clamped.

    Returns:
        int: The clamped value.
    """

    if input < min:
        return min
    elif input > max:
        return max
    return input


@njit
def clamp_double(min, max, input):
    """
    Clamps a double value between a minimum and maximum value.

    Args:
        min (float): The minimum value to clamp to.
        max (float): The maximum value to clamp to.
        input (float): The input value to be clamped.

    Returns:
        float: The clamped value.
    """


    if input < min:
        return min
    elif input > max:
        return max
    return input


@njit
def sanitize_degrees_int(degrees):
    """
    Sanitizes an integer value representing degrees by ensuring it falls within the range of 0 to 359.

    Args:
        degrees (int): The input value representing degrees.

    Returns:
        int: The sanitized value of degrees within the range of 0 to 359.
    """


    degrees = degrees % 360

    if degrees < 0:
        degrees = degrees + 360

    return degrees


@njit
def sanitize_degrees_double(degrees):
    """
    Sanitizes a floating-point value representing degrees by ensuring it falls within the range of 0.0 to 359.0.

    Args:
        degrees (float): The input value representing degrees.

    Returns:
        float: The sanitized value of degrees within the range of 0.0 to 359.0.
    """


    degrees = degrees % 360.0

    if degrees < 0:
        degrees = degrees + 360.0

    return degrees


@njit
def difference_degrees(a, b):
    """
    Calculates the difference in degrees between two values.

    Args:
        a (float): The first value in degrees.
        b (float): The second value in degrees.

    Returns:
        float: The difference in degrees between the two values.
    """

    return 180.0 - np.abs(np.abs(a - b) - 180.0)


@njit
def matrix_multiply(row, matrix):
    """
    Multiplies a row vector by a 3x3 matrix.

    Args:
        row (List[float]): The row vector to be multiplied.
        matrix (List[List[float]]): The 3x3 matrix to multiply the row vector with.

    Returns:
        np.ndarray: The result of multiplying the row vector by the matrix.
    """

    return np.dot(row, matrix)
