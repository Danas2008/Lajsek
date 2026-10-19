"""Kontext pro dvojjazyčnou hlavičku (přepínač jazyka + hreflang)."""

from django.conf import settings
from django.urls import translate_url
from django.utils.translation import get_language

from .seo import absolute


def language_links(request):
    """Adresy aktuální stránky ve všech jazycích, pro přepínač i hreflang.

    ``url`` drží i query string (přepínač jazyka nesmí ztratit např.
    ?obraz=K1), ``href`` je kanonická absolutní adresa bez parametrů.
    """
    current = get_language()
    full_path = request.get_full_path()
    alternates = []
    for code, name in settings.LANGUAGES:
        alternates.append({
            'code': code,
            'name': name,
            'url': translate_url(full_path, code),
            'href': absolute(translate_url(request.path, code)),
            'is_current': code == current,
        })
    return {
        'language_alternates': alternates,
        'x_default_href': absolute(translate_url(request.path, settings.LANGUAGE_CODE)),
        'canonical_href': absolute(request.path),
        'current_language': current,
    }


def site(request):
    return {
        'SITE_URL': settings.SITE_URL,
        'PLAUSIBLE_DOMAIN': settings.PLAUSIBLE_DOMAIN,
        'UMAMI_SRC': settings.UMAMI_SRC,
        'UMAMI_ID': settings.UMAMI_ID,
    }
