from ..utils.color_utils import linearized, argb_from_xyz
from ..utils.math_utils import signum
from ..hct.viewing_conditions import ViewingConditions
import math

import numpy as np
from numba import njit

# /**
#  * CAM16, a color appearance model. Colors are not just defined by their hex
#  * code, but rather, a hex code and viewing conditions.
#  *
#  * CAM16 instances also have coordinates in the CAM16-UCS space, called J*, a*,
#  * b*, or jstar, astar, bstar in code. CAM16-UCS is included in the CAM16
#  * specification, and should be used when measuring distances between colors.
#  *
#  * In traditional color spaces, a color can be identified solely by the
#  * observer's measurement of the color. Color appearance models such as CAM16
#  * also use information about the environment where the color was
#  * observed, known as the viewing conditions.
#  *
#  * For example, white under the traditional assumption of a midday sun white
#  * point is accurately measured as a slightly chromatic blue by CAM16. (roughly,
#  * hue 203, chroma 3, lightness 100)
#  */
class Cam16:
    # /**
    #  * All of the CAM16 dimensions can be calculated from 3 of the dimensions, in
    #  * the following combinations:
    #  *      -  {j or q} and {c, m, or s} and hue
    #  *      - jstar, astar, bstar
    #  * Prefer using a static method that constructs from 3 of those dimensions.
    #  * This constructor is intended for those methods to use to return all
    #  * possible dimensions.
    #  *
    #  * @param hue
    #  * @param chroma informally, colorfulness / color intensity. like saturation
    #  *     in HSL, except perceptually accurate.
    #  * @param j lightness
    #  * @param q brightness ratio of lightness to white point's lightness
    #  * @param m colorfulness
    #  * @param s saturation ratio of chroma to white point's chroma
    #  * @param jstar CAM16-UCS J coordinate
    #  * @param astar CAM16-UCS a coordinate
    #  * @param bstar CAM16-UCS b coordinate
    #  */
    def __init__(self, hue, chroma, j, q, m, s, jstar, astar, bstar):
        self.hue = hue
        self.chroma = chroma
        self.j = j
        self.q = q
        self.m = m
        self.s = s
        self.jstar = jstar
        self.astar = astar
        self.bstar = bstar

    # /**
    #  * CAM16 instances also have coordinates in the CAM16-UCS space, called J*,
    #  * a*, b*, or jstar, astar, bstar in code. CAM16-UCS is included in the CAM16
    #  * specification, and is used to measure distances between colors.
    #  */
    def distance(self, other):
        dJ = self.jstar - other.jstar
        dA = self.astar - other.astar
        dB = self.bstar - other.bstar
        dEPrime = math.sqrt(dJ * dJ + dA * dA + dB * dB)
        return 1.41 * pow(dEPrime, 0.63)


    @staticmethod
    def from_int(argb):
        """
        Convert an ARGB color value to a Cam16 color representation.

        Args:
            argb (int): The ARGB color value represented as an integer.

        Returns:
            tuple: The Cam16 color representation as a tuple of (jstar, astar, bstar).

        Examples:
            >>> from_int(16777215)
            (0.9999999999999999, 0.0, 0.0)
            >>> from_int(65280)
            (0.9999999999999999, 0.0, 0.0)
        """

        return Cam16.from_int_in_viewing_conditions(argb, ViewingConditions.DEFAULT)


    @staticmethod
    @njit
    def from_int_in_viewing_conditions(argb, viewing_conditions):
        """
        Convert an ARGB color value to a Cam16 color representation in the specified viewing conditions.

        Args:
            argb (int): The ARGB color value represented as an integer.
            viewing_conditions (ViewingConditions): The viewing conditions for the conversion.

        Returns:
            Cam16: The Cam16 color representation.

        Examples:
            >>> from_int_in_viewing_conditions(16777215, Viewing_conditions.DEFAULT)
            Cam16(hue=0.0, chroma=0.0, jstar=0.9999999999999999, q=0.0, m=0.0, s=0.0, astar=0.0, bstar=0.0)
            >>> from_int_in_viewing_conditions(65280, Viewing_conditions.DEFAULT)
            Cam16(hue=0.0, chroma=0.0, jstar=0.9999999999999999, q=0.0, m=0.0, s=0.0, astar=0.0, bstar=0.0)
        """


        red = (argb & 0x00ff0000) >> 16
        green = (argb & 0x0000ff00) >> 8
        blue = (argb & 0x000000ff)
        redL = linearized(red)
        greenL = linearized(green)
        blueL = linearized(blue)
        x = 0.41233895 * redL + 0.35762064 * greenL + 0.18051042 * blueL
        y = 0.2126 * redL + 0.7152 * greenL + 0.0722 * blueL
        z = 0.01932141 * redL + 0.11916382 * greenL + 0.95034478 * blueL
        rC = 0.401288 * x + 0.650173 * y - 0.051461 * z
        gC = -0.250268 * x + 1.204414 * y + 0.045854 * z
        bC = -0.002079 * x + 0.048952 * y + 0.953127 * z
        rD = viewing_conditions.rgbD[0] * rC
        gD = viewing_conditions.rgbD[1] * gC
        bD = viewing_conditions.rgbD[2] * bC
        rAF = pow((viewing_conditions.fl * abs(rD)) / 100.0, 0.42)
        gAF = pow((viewing_conditions.fl * abs(gD)) / 100.0, 0.42)
        bAF = pow((viewing_conditions.fl * abs(bD)) / 100.0, 0.42)
        rA = (signum(rD) * 400.0 * rAF) / (rAF + 27.13)
        gA = (signum(gD) * 400.0 * gAF) / (gAF + 27.13)
        bA = (signum(bD) * 400.0 * bAF) / (bAF + 27.13)
        a = (11.0 * rA + -12.0 * gA + bA) / 11.0
        b = (rA + gA - 2.0 * bA) / 9.0
        u = (20.0 * rA + 20.0 * gA + 21.0 * bA) / 20.0
        p2 = (40.0 * rA + 20.0 * gA + bA) / 20.0
        atan2 = math.atan2(b, a)
        atanDegrees = (atan2 * 180.0) / math.pi
        hue =  atanDegrees + 360.0 if atanDegrees < 0 else atanDegrees - 360.0 if atanDegrees >= 360 else atanDegrees
        hueRadians = (hue * math.pi) / 180.0
        ac = p2 * viewing_conditions.nbb
        j = 100.0 * pow(ac / viewing_conditions.aw, viewing_conditions.c * viewing_conditions.z)
        q = (4.0 / viewing_conditions.c) * math.sqrt(j / 100.0) * (viewing_conditions.aw + 4.0) * viewing_conditions.fLRoot
        huePrime = hue + 360 if hue < 20.14 else hue
        eHue = 0.25 * (math.cos((huePrime * math.pi) / 180.0 + 2.0) + 3.8)
        p1 = (50000.0 / 13.0) * eHue * viewing_conditions.nc * viewing_conditions.ncb
        t = (p1 * math.sqrt(a * a + b * b)) / (u + 0.305)
        alpha = pow(t, 0.9) * pow(1.64 - pow(0.29, viewing_conditions.n), 0.73)
        c = alpha * math.sqrt(j / 100.0)
        m = c * viewing_conditions.fLRoot
        s = 50.0 * math.sqrt((alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0))
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hueRadians)
        bstar = mstar * math.sin(hueRadians)
        return Cam16(hue, c, j, q, m, s, jstar, astar, bstar)

    # /**
    #  * @param j CAM16 lightness
    #  * @param c CAM16 chroma
    #  * @param h CAM16 hue
    #  */
    @staticmethod
    def fromJch(j, c, h):
        return Cam16.fromJch_in_viewing_conditions(j, c, h, ViewingConditions.DEFAULT)

    # /**
    #  * @param j CAM16 lightness
    #  * @param c CAM16 chroma
    #  * @param h CAM16 hue
    #  * @param viewing_conditions Information about the environment where the color
    #  *     was observed.
    #  */
    @staticmethod
    def fromJch_in_viewing_conditions(j, c, h, viewing_conditions):
        q = (4.0 / viewing_conditions.c) * math.sqrt(j / 100.0) * (viewing_conditions.aw + 4.0) * viewing_conditions.fLRoot
        m = c * viewing_conditions.fLRoot
        alpha = c / math.sqrt(j / 100.0)
        s = 50.0 * math.sqrt((alpha * viewing_conditions.c) / (viewing_conditions.aw + 4.0))
        hueRadians = (h * math.pi) / 180.0
        jstar = ((1.0 + 100.0 * 0.007) * j) / (1.0 + 0.007 * j)
        mstar = (1.0 / 0.0228) * math.log(1.0 + 0.0228 * m)
        astar = mstar * math.cos(hueRadians)
        bstar = mstar * math.sin(hueRadians)
        return Cam16(h, c, j, q, m, s, jstar, astar, bstar)

    # /**
    #  * @param jstar CAM16-UCS lightness.
    #  * @param astar CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the Y axis.
    #  * @param bstar CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the X axis.
    #  */
    @staticmethod
    def from_ucs(jstar, astar, bstar):
        return Cam16.fromUcs_in_viewing_conditions(jstar, astar, bstar, ViewingConditions.DEFAULT)

    # /**
    #  * @param jstar CAM16-UCS lightness.
    #  * @param astar CAM16-UCS a dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the Y axis.
    #  * @param bstar CAM16-UCS b dimension. Like a* in L*a*b*, it is a Cartesian
    #  *     coordinate on the X axis.
    #  * @param viewing_conditions Information about the environment where the color
    #  *     was observed.
    #  */
    @staticmethod
    def fromUcs_in_viewing_conditions(jstar, astar, bstar, viewing_conditions):
        a = astar
        b = bstar
        m = math.sqrt(a * a + b * b)
        M = (math.exp(m * 0.0228) - 1.0) / 0.0228
        c = M / viewing_conditions.fLRoot
        h = math.atan2(b, a) * (180.0 / math.pi)
        if (h < 0.0):
            h += 360.0
        j = jstar / (1 - (jstar - 100) * 0.007)
        return Cam16.fromJch_in_viewing_conditions(j, c, h, viewing_conditions)

    # /**
    #  *  @return ARGB representation of color, assuming the color was viewed in
    #  *     default viewing conditions, which are near-identical to the default
    #  *     viewing conditions for sRGB.
    #  */
    def to_int(self):
        return self.viewed(ViewingConditions.DEFAULT)

    # /**
    #  * @param viewing_conditions Information about the environment where the color
    #  *     will be viewed.
    #  * @return ARGB representation of color
    #  */
    def viewed(self, viewing_conditions):
        alpha =  0.0 if self.chroma == 0.0 or self.j == 0.0 else self.chroma / math.sqrt(self.j / 100.0)
        t = pow(alpha / pow(1.64 - pow(0.29, viewing_conditions.n), 0.73), 1.0 / 0.9)
        hRad = (self.hue * math.pi) / 180.0
        eHue = 0.25 * (math.cos(hRad + 2.0) + 3.8)
        ac = viewing_conditions.aw * pow(self.j / 100.0, 1.0 / viewing_conditions.c / viewing_conditions.z)
        p1 = eHue * (50000.0 / 13.0) * viewing_conditions.nc * viewing_conditions.ncb
        p2 = ac / viewing_conditions.nbb
        hSin = math.sin(hRad)
        hCos = math.cos(hRad)
        gamma = (23.0 * (p2 + 0.305) * t) / (23.0 * p1 + 11.0 * t * hCos + 108.0 * t * hSin)
        a = gamma * hCos
        b = gamma * hSin
        rA = (460.0 * p2 + 451.0 * a + 288.0 * b) / 1403.0
        gA = (460.0 * p2 - 891.0 * a - 261.0 * b) / 1403.0
        bA = (460.0 * p2 - 220.0 * a - 6300.0 * b) / 1403.0
        rCBase = max(0, (27.13 * abs(rA)) / (400.0 - abs(rA)))
        rC = signum(rA) * (100.0 / viewing_conditions.fl) * pow(rCBase, 1.0 / 0.42)
        gCBase = max(0, (27.13 * abs(gA)) / (400.0 - abs(gA)))
        gC = signum(gA) * (100.0 / viewing_conditions.fl) * pow(gCBase, 1.0 / 0.42)
        bCBase = max(0, (27.13 * abs(bA)) / (400.0 - abs(bA)))
        bC = signum(bA) * (100.0 / viewing_conditions.fl) * pow(bCBase, 1.0 / 0.42)
        rF = rC / viewing_conditions.rgbD[0]
        gF = gC / viewing_conditions.rgbD[1]
        bF = bC / viewing_conditions.rgbD[2]
        x = 1.86206786 * rF - 1.01125463 * gF + 0.14918677 * bF
        y = 0.38752654 * rF + 0.62144744 * gF - 0.00897398 * bF
        z = -0.01584150 * rF - 0.03412294 * gF + 1.04996444 * bF
        return argb_from_xyz(x, y, z)
