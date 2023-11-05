from ..blend.blend import Blend
from ..palettes.core_palette import CorePalette
from ..scheme.scheme import Scheme
from .image_utils import SourceColorFromImage

def custom_color(source, color):
    """
    Customizes a color based on the provided source and color.

    Args:
        source: The source color to customize from.
        color: The color object containing the value and blend information.

    Returns:
        A dictionary containing the customized color and its variations.

    Examples:
        >>> source = "#FF0000"
        >>> color = {"value": "#00FF00", "blend": True}
        >>> custom_color(source, color)
        {
            "color": {"value": "#00FF00", "blend": True},
            "value": "#00FF00",
            "light": {
                "color": "#00AA00",
                "onColor": "#00FF00",
                "colorContainer": "#00DD00",
                "onColorContainer": "#000000",
            },
            "dark": {
                "color": "#005500",
                "onColor": "#00FF00",
                "colorContainer": "#008800",
                "onColorContainer": "#00DD00",
            },
        }
    """
    
    value = color["value"]
    from_v = value
    to = source

    if (color["blend"]):
        value = Blend.harmonize(from_v, to)

    palette = CorePalette.of(value)
    tones = palette.a1

    return {
        "color": color,
        "value": value,
        "light": {
            "color": tones.tone(40),
            "onColor": tones.tone(100),
            "colorContainer": tones.tone(90),
            "onColorContainer": tones.tone(10),
        },
        "dark": {
            "color": tones.tone(80),
            "onColor": tones.tone(20),
            "colorContainer": tones.tone(30),
            "onColorContainer": tones.tone(90),
        },
    }


def theme_from_source_color(source, custom_colors=None):
    """
    Generates a theme based on the provided source color.

    Args:
        source: The source color to generate the theme from.
        custom_colors: Optional list of custom colors to apply to the theme.

    Returns:
        A dictionary containing the generated theme with color schemes, palettes, and custom colors.

    Examples:
        >>> source = "#FF0000"
        >>> custom_colors = [
        ...     {"value": "#00FF00", "blend": True},
        ...     {"value": "#0000FF", "blend": False}
        ... ]
        >>> theme_from_source_color(source, custom_colors)
        {
            "source": "#FF0000",
            "schemes": {
                "light": {...},
                "dark": {...}
            },
            "palettes": {...},
            "custom_colors": [
                {...},
                {...}
            ]
        }
    """

    if custom_colors is None:
        custom_colors = []

    palette = CorePalette.of(source)

    return {
        "source": source,
        "schemes": {
            "light": Scheme.light(source),
            "dark": Scheme.dark(source),
        },
        "palettes": {
            "primary": palette.a1,
            "secondary": palette.a2,
            "tertiary": palette.a3,
            "neutral": palette.n1,
            "neutralVariant": palette.n2,
            "error": palette.error,
        },
        "custom_colors": [custom_color(source, c) for c in custom_colors]
    }


def theme_from_image(image, custom_colors=None):
    """
    Generates a theme based on the provided image.

    Args:
        image: The image to extract the source color from.
        custom_colors: Optional list of custom colors to apply to the theme.

    Returns:
        A dictionary containing the generated theme with color schemes, palettes, and custom colors.

    Examples:
        >>> image = Image.open("path/to/image.jpg")
        >>> custom_colors = [
        ...     {"value": "#00FF00", "blend": True},
        ...     {"value": "#0000FF", "blend": False}
        ... ]
        >>> theme_from_image(image, custom_colors)
        {
            "source": "#FF0000",
            "schemes": {
                "light": {...},
                "dark": {...}
            },
            "palettes": {...},
            "custom_colors": [
                {...},
                {...}
            ]
        }
    """

    if custom_colors is None:
        custom_colors = []

    source = SourceColorFromImage(image)
    return theme_from_source_color(source, custom_colors)
