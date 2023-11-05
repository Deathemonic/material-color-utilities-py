# material-color-utilities-py

Python port of material-color-utilities used for Material You colors

Forked from: https://github.com/avanisubbiah/material-color-utilities-python
Original source code: https://github.com/material-foundation/material-color-utilities

NOTE: This is a rewrite of the material-color-utilities-python module which is a port of Javascript to Python. Because it's a port there some Javascript leftovers that are still in, so this is a proper reimprementation of material-color-utilities in python with proper docstrings proper naming convention, optimization and refactoring, etc.

## Build and install

Pip:

```shell
pip install material-color-utilities-py
```

## Usage examples for Themeing

Theme from color:

``` python
from material_color_utilities import theme_from_source_color, argb_from_hex

theme = theme_from_source_color(argb_from_hex('#4285f4'))

print(theme)
```

Color from image:

``` python
from material_color_utilities_python import Image, SourceColorFromImage, hex_from_argb

img = Image.open('path/to/image.png')
argb = SourceColorFromImage(img)

print(hex_from_argb(argb))
```

Theme from image:

``` python
from material_color_utilities_python import Image, theme_from_image

img = Image.open('/path/to/image')
basewidth = 64
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize),Image.Resampling.LANCZOS)
print(theme_from_image(img))

print(theme)
```
