"""Render glyphs in the style of the Chinese patch's font atlas (Microsoft YaHei).

The font is read from the user's own Windows installation; no font data is shipped.
Parameters were fitted against the patch's existing glyphs.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_font = None


def set_font(path):
    global _font
    _font = ImageFont.truetype(path, 106)


def _hi(ch, stroke=0):
    im = Image.new('L', (160, 160), 0)
    ImageDraw.Draw(im).text((23, 0), ch, font=_font, fill=255, stroke_width=stroke, stroke_fill=255)
    return im


def _small(a80, flt, k):
    r = np.array(Image.fromarray(np.clip(a80, 0, 255).astype(np.uint8)).resize((15, 15), flt), np.float32) * k
    g = np.zeros((24, 24), np.float32); g[3:18, 3:18] = r
    return np.clip(g, 0, 255)


def render(ch):
    """Body and outline layers for the 40px ('80') and 24px ('14pt') atlases."""
    b80 = np.clip(np.array(_hi(ch).resize((40, 40), Image.LANCZOS), np.float32) * 1.1, 0, 255)
    g80 = np.clip(np.array(_hi(ch, 8).resize((40, 40), Image.LANCZOS), np.float32) * 1.2, 0, 255)
    return dict(b80=b80, g80=g80, b14=_small(b80, Image.BICUBIC, 1.0), g14=_small(g80, Image.BILINEAR, 1.2))
