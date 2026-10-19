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
from django.utils.translation import get_language, gettext_noop

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


def catalog():
    """Údaje o katalogu odečtené z PDF příkazem make_catalog_preview."""
    return _data().get('catalog') or {}


def page_images(page):
    """Obrázky dané stránky jako [{'caption', 'image'}] (cesty v MEDIA_URL)."""
    return _data().get('page_images', {}).get(page, [])


def has_translation(page):
    """True, pokud má stránka anglický text (bez ohledu na aktuální jazyk)."""
    return bool(_data().get('texts_en', {}).get(page))


def portrait_path():
    """Cesta k portrétu autora v MEDIA_URL (úvodní obrázek původního webu)."""
    images = page_images('uvod')
    return images[0]['image'] if images else None


# Životopis po kapitolách: (kotva, nadpis, indexy odstavců). První odstavec
# původního textu spojuje dětství a odboj, proto se dělí podle věty níže.
_ODBOJ_START = 'Během 2. světové války'
BIOGRAPHY_SECTIONS = [
    ('detstvi-a-kutna-hora', gettext_noop('Dětství a Kutná Hora'), ['0a']),
    ('odboj', gettext_noop('Odboj'), ['0b']),
    ('studia', gettext_noop('Po válce a studia'), [1, 2]),
    ('pedagog-a-sups', gettext_noop('Pedagog a SUPŠ'), [3]),
    ('skupina-smer', gettext_noop('Skupina Směr'), [4]),
    ('pozdni-tvorba', gettext_noop('Pozdní tvorba'), [5, 6, 7]),
]


def biography_sections():
    """Odstavce stránky Život rozdělené do kapitol s nadpisem a kotvou.

    Nadpisy se překládají v šabloně ({% trans %}); text zůstává v jazyce,
    ve kterém je k dispozici. Kdyby se počet odstavců změnil, zbytek se
    připojí k poslední kapitole — žádný text se neztratí.
    """
    texts = list(paragraphs('zivot'))
    if not texts:
        return []
    first = texts[0]
    split_at = first.find(_ODBOJ_START)
    parts = {
        '0a': first[:split_at].strip() if split_at > 0 else first,
        '0b': first[split_at:].strip() if split_at > 0 else '',
    }
    for index, text in enumerate(texts[1:], start=1):
        parts[index] = text

    used, sections = set(), []
    for anchor, heading, keys in BIOGRAPHY_SECTIONS:
        texts = [parts[key] for key in keys if parts.get(key)]
        used.update(keys)
        if texts:
            sections.append({'id': anchor, 'heading': heading, 'paragraphs': texts})
    leftover = [text for key, text in parts.items() if key not in used and text]
    if leftover and sections:
        sections[-1]['paragraphs'].extend(leftover)
    return sections

