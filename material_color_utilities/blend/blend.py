from ..hct.cam16 import Cam16
from ..hct.hct import Hct
from ..utils.color_utils import lstar_from_argb
from ..utils.math_utils import difference_degrees, sanitize_degrees_double

import numpy as np
from numba import njit


class Blend:
    """
    Functions for blending in HCT and CAM16.
    """
    @staticmethod
    def harmonize(designColor, sourceColor):
        """
        Harmonize the design color with the source color.

        Args:
            designColor (int): The design color represented as an integer.
            sourceColor (int): The source color represented as an integer.

        Returns:
            int: The harmonized color represented as an integer.

        Examples:
            >>> harmonize(16777215, 65280)
            16777215
            >>> harmonize(65280, 16777215)
            16777215
        """

        from_hct = Hct.from_int(designColor)
        to_hct = Hct.from_int(sourceColor)
        difference_degrees_v = difference_degrees(from_hct.hue, to_hct.hue)
        rotation_degrees = min(difference_degrees_v * 0.5, 15.0)
        output_hue = sanitize_degrees_double(from_hct.hue + rotation_degrees * Blend.rotation_direction(from_hct.hue, to_hct.hue))
        return Hct.from_hct(output_hue, from_hct.chroma, from_hct.tone).to_int()


    @staticmethod
    def hct_hue(from_v, to, amount):
        """
        Calculate the hue value of a color blend between two colors.

        Args:
            from_v (int): The starting color represented as an integer.
            to (int): The target color represented as an integer.
            amount (float): The amount of blend between the two colors.

        Returns:
            int: The blended color represented as an integer.

        Examples:
            >>> hct_hue(16777215, 65280, 0.5)
            16777215
            >>> hct_hue(65280, 16777215, 0.5)
            16777215
        """

        ucs = Blend.cam16_ucs(from_v, to, amount)
        ucs_cam = Cam16.from_int(ucs)
        from_cam = Cam16.from_int(from_v)
        blended = Hct.from_hct(ucs_cam.hue, from_cam.chroma, lstar_from_argb(from_v))
        return blended.toInt()


    @staticmethod
    def cam16_ucs(from_v, to, amount):
        """
        Calculate the UCS (Uniform Color Space) representation of a color blend between two colors.

        Args:
            from_v (int): The starting color represented as an integer.
            to (int): The target color represented as an integer.
            amount (float): The amount of blend between the two colors.

        Returns:
            int: The blended color represented as an integer in the UCS color space.

        Examples:
            >>> cam16_ucs(16777215, 65280, 0.5)
            16777215
            >>> cam16_ucs(65280, 16777215, 0.5)
            16777215
        """

        from_cam = Cam16.from_int(from_v)
        to_cam = Cam16.from_int(to)
        fromj = from_cam.jstar
        froma = from_cam.astar
        fromb = from_cam.bstar
        toj = to_cam.jstar
        toa = to_cam.astar
        toa = to_cam.bstar
        jstar = fromj + (toj - fromj) * amount
        astar = froma + (toa - froma) * amount
        bstar = fromb + (toa - fromb) * amount
        return Cam16.from_ucs(jstar, astar, bstar).to_int()


    @staticmethod
    @njit
    def rotation_direction(from_v, to):
        """
        Determine the rotation direction between two angles.

        Args:
            from_v (float): The starting angle in degrees.
            to (float): The target angle in degrees.

        Returns:
            float: The rotation direction as 1.0 for clockwise or -1.0 for counterclockwise.

        Examples:
            >>> rotation_direction(0.0, 90.0)
            1.0
            >>> rotation_direction(180.0, 90.0)
            -1.0
        """

        values = np.array([to - from_v, to - from_v + 360.0, to - from_v - 360.0])
        abs_values = np.abs(values)
        min_index = np.argmin(abs_values)
        return np.sign(values[min_index])
