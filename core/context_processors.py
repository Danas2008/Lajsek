"""Kontext pro dvojjazyčnou hlavičku (přepínač jazyka + hreflang)."""

from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language


def language_links(request):
    """Adresy aktuální stránky ve všech jazycích, pro přepínač i hreflang."""
    current = get_language()
    path = request.get_full_path()
    alternates = []
    for code, name in settings.LANGUAGES:
        alternates.append({
            'code': code,
            'name': name,
            'url': translate_url(path, code),
            'is_current': code == current,
        })
    return {
        'language_alternates': alternates,
        'current_language': current,
    }
