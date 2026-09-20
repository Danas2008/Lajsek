"""Pomocné tagy pro dvojjazyčný obsah.

Obsahová pole (texty o životě, popisy výstav, citáty) se nepřekládají
strojově. Pokud anglická varianta chybí, zobrazí se český originál
a šablona k němu doplní poznámku.
"""

from django import template
from django.utils.translation import get_language

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
