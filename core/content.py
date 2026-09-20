"""Přístup k textům převzatým z původního webu lajsek.cz.

Texty stránek Život / Dílo / Katalog jsou statické, proto nejsou v databázi,
ale načítají se z data/wp_content.json (výsledek přenosu z WordPressu).

Anglické verze se sem doplňují ručně do klíče ``texts_en``. Strojový překlad
záměrně neprobíhá — jde o historické a kulturní texty, kde by zkreslil význam.
Dokud překlad chybí, zobrazí se český originál s poznámkou pro návštěvníka.
"""

import json
from functools import lru_cache

from django.conf import settings
from django.utils.translation import get_language

DATA_FILE = settings.BASE_DIR / 'data' / 'wp_content.json'


@lru_cache(maxsize=1)
def _data():
    with open(DATA_FILE, encoding='utf-8') as fh:
        return json.load(fh)


def paragraphs(page):
    """Odstavce stránky v aktuálním jazyce, s češtinou jako záložní variantou."""
    data = _data()
    if get_language() == 'en':
        english = data.get('texts_en', {}).get(page)
        if english:
            return english
    return data.get('texts', {}).get(page, [])


def is_untranslated(page):
    """True, pokud jsme v EN verzi a anglický text zatím chybí."""
    if get_language() != 'en':
        return False
    return not _data().get('texts_en', {}).get(page)


def page_images(page):
    """Obrázky dané stránky jako [{'caption', 'image'}] (cesty v MEDIA_URL)."""
    return _data().get('page_images', {}).get(page, [])
