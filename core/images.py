"""Rozměry obrázků v MEDIA_ROOT pro width/height (CLS) a og:image.

Čte se jen hlavička souboru a výsledek se pamatuje po dobu běhu procesu.
Chybějící soubor (např. v testech) vrátí None a šablona atributy vynechá.
"""

import os
from functools import lru_cache

from django.conf import settings
from PIL import Image

# EXIF orientace, při kterých je fotografie otočená o 90° — šířka a výška
# v hlavičce jsou pak prohozené oproti tomu, jak se obrázek zobrazí.
_ROTATED = {5, 6, 7, 8}


@lru_cache(maxsize=4096)
def image_size(relative_path):
    path = os.path.join(settings.MEDIA_ROOT, relative_path)
    try:
        with Image.open(path) as im:
            width, height = im.size
            if im.getexif().get(0x0112) in _ROTATED:
                width, height = height, width
            return width, height
    except (OSError, ValueError):
        return None


def scaled_size(relative_path, max_width):
    """Rozměr zmenšeniny o šířce max_width (originál se nezvětšuje)."""
    size = image_size(relative_path)
    if not size:
        return None
    width, height = size
    if width <= max_width:
        return width, height
    return max_width, round(height * max_width / width)
