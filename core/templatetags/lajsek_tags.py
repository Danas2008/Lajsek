"""Pomocné tagy pro dvojjazyčný obsah.

Obsahová pole (texty o životě, popisy výstav, citáty) se nepřekládají
strojově. Pokud anglická varianta chybí, zobrazí se český originál
a šablona k němu doplní poznámku.
"""

import json

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

from core.images import image_size

register = template.Library()


@register.simple_tag
def translated(obj, field):
    """Anglická varianta pole, je-li vyplněná; jinak český originál."""
    if get_language() == 'en':
        english = getattr(obj, f'{field}_en', '')
        if english:
            return english
    return getattr(obj, field, '')


@register.simple_tag
def is_untranslated(obj, field):
    """True, pokud jsme v EN verzi a pole nemá anglický překlad."""
    if get_language() != 'en':
        return False
    return not getattr(obj, f'{field}_en', '')


@register.simple_tag
def jsonld(*items):
    """Vypíše slovníky schema.org jako <script type="application/ld+json">.

    json.dumps + escapování „<“ zaručí, že text z databáze nemůže ukončit
    značku <script> ani rozbít JSON.
    """
    blocks = []
    for item in items:
        for data in (item if isinstance(item, (list, tuple)) else [item]):
            if not data:
                continue
            payload = json.dumps(data, ensure_ascii=False, indent=2)
            payload = payload.replace('<', '\u003c').replace('>', '\u003e').replace('&', '\u0026')
            blocks.append(f'<script type="application/ld+json">\n{payload}\n</script>')
    return mark_safe('\n'.join(blocks))


@register.simple_tag
def media_size(relative_path):
    """(šířka, výška) obrázku v MEDIA_ROOT pro atributy width/height."""
    return image_size(relative_path)
