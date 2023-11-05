from .color_utils import red_from_argb, green_from_argb, blue_from_argb, rshift

def hex_from_argb(argb):
    r = red_from_argb(argb)
    g = green_from_argb(argb)
    b = blue_from_argb(argb)

    return f'#{r:02x}{g:02x}{b:02x}'


def parse_int_hex(value):
    return int(value, 16)


def argb_from_hex(hex):
    hex = hex.replace('#', '')
    isThree = len(hex) == 3
    isSix = len(hex) == 6
    isEight = len(hex) == 8
    if (not isThree and not isSix and not isEight):
        raise Exception('unexpected hex ' + hex)
    
    r = 0
    g = 0
    b = 0
    if (isThree):
        r = parse_int_hex(hex[0:1]*2)
        g = parse_int_hex(hex[1:2]*2)
        b = parse_int_hex(hex[2:3]*2)
    elif (isSix):
        r = parse_int_hex(hex[0:2])
        g = parse_int_hex(hex[2:4])
        b = parse_int_hex(hex[4:6])
    elif (isEight):
        r = parse_int_hex(hex[2:4])
        g = parse_int_hex(hex[4:6])
        b = parse_int_hex(hex[6:8])
    
    return rshift(((255 << 24) | ((r & 0x0ff) << 16) | ((g & 0x0ff) << 8) | (b & 0x0ff)), 0)
