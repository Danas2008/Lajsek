"""Trvalá přesměrování starých adres a sjednocení tvaru URL.

LegacyRedirectMiddleware — adresy původního WordPress webu
(?page_id=, ?p=, ?attachment_id=, /wp-content/uploads/…) vedou 301 na
odpovídající stránku nebo soubor nového webu. Mapa je v
data/wp_redirects.json. Zaniklé RSS kanály vrací 410 Gone, aby je
vyhledávače přestaly zkoušet.

LowercaseRedirectMiddleware — /Obrazy/ → /obrazy/ (301), ať nevznikají
duplicitní URL. Soubory v /media/ a /static/ a admin se nemění, názvy
souborů rozlišují velikost písmen.
"""

import json
import os
import re
import unicodedata
from functools import lru_cache
from urllib.parse import unquote

from django.conf import settings
from django.http import HttpResponseGone, HttpResponsePermanentRedirect
from django.urls import NoReverseMatch, reverse
from django.utils.encoding import iri_to_uri

DATA_FILE = settings.BASE_DIR / 'data' / 'wp_redirects.json'

# název-300x225.jpg → název (WordPress přidává rozměr zmenšeniny)
_UPLOAD_RE = re.compile(r'^/wp-content/uploads/\d{4}/\d{2}/(?P<name>.+?)(?:-\d+x\d+)?\.\w+$')


@lru_cache(maxsize=1)
def _map():
    with open(DATA_FILE, encoding='utf-8') as fh:
        return json.load(fh)


def _painting(code):
    from gallery.models import Painting
    return Painting.objects.select_related('category').filter(title=code).first()


def _resolve(target):
    """Cíl z mapy → URL nového webu, nebo None."""
    from gallery.models import Category

    if 'painting' in target:
        painting = _painting(target['painting'])
        return painting.get_absolute_url() if painting else None
    if 'painting_image' in target:
        painting = _painting(target['painting_image'])
        return painting.image.url if painting else None
    if 'category' in target:
        category = Category.objects.filter(slug=target['category']).first()
        return category.get_absolute_url() if category else None
    if 'media' in target:
        return settings.MEDIA_URL + target['media']
    if 'url_name' in target:
        return reverse(target['url_name'])
    return None


def legacy_target(path, query):
    """URL, kam vede stará adresa; '' = zaniklá (410); None = nejde o starou adresu."""
    data = _map()

    if path == '/' and query:
        page_id = query.get('page_id') or query.get('p')
        if 'feed' in query or 'rest_route' in query:
            return ''
        if page_id in data['pages']:
            name = data['pages'][page_id]
            if name.startswith('category:'):
                return _resolve({'category': name.split(':', 1)[1]})
            return reverse(name)
        attachment = query.get('attachment_id')
        if attachment in data['attachments']:
            return _resolve(data['attachments'][attachment])
        return None

    match = _UPLOAD_RE.match(path)
    if match:
        name = unicodedata.normalize('NFC', unquote(match.group('name')))
        target = data['uploads'].get(name)
        return _resolve(target) if target else None

    if path.startswith('/feed') or path.startswith('/comments/feed'):
        return ''
    return None


class LegacyRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/' and request.GET or request.path.startswith(('/wp-', '/feed', '/comments/feed')):
            try:
                target = legacy_target(request.path, request.GET)
            except NoReverseMatch:
                target = None
            if target == '':
                return HttpResponseGone()
            if target:
                return HttpResponsePermanentRedirect(iri_to_uri(target))
        return self.get_response(request)


class LowercaseRedirectMiddleware:
    SKIP = ('/admin/', '/media/', '/static/', '/wp-')

    def __init__(self, get_response):
        self.get_response = get_response
        self.skip = self.SKIP + tuple(
            '/' + prefix.strip('/') + '/'
            for prefix in (settings.MEDIA_URL, settings.STATIC_URL) if prefix
        )

    def __call__(self, request):
        path = request.path
        if path != path.lower() and not path.startswith(self.skip):
            query = request.META.get('QUERY_STRING', '')
            target = iri_to_uri(path.lower()) + (f'?{query}' if query else '')
            return HttpResponsePermanentRedirect(target)
        return self.get_response(request)


def legacy_redirect_table():
    """Seznam (stará URL, nová URL) pro kontrolu a dokumentaci."""
    data = _map()
    rows = []
    for page_id in data['pages']:
        for param in ('page_id', 'p'):
            rows.append((f'/?{param}={page_id}', legacy_target('/', {param: page_id})))
    for attachment in data['attachments']:
        rows.append((f'/?attachment_id={attachment}',
                     legacy_target('/', {'attachment_id': attachment})))
    for name in data['uploads']:
        ext = os.path.splitext(_resolve(data['uploads'][name]) or '')[1] or '.jpg'
        old = f'/wp-content/uploads/2016/09/{name}{ext}'
        rows.append((old, legacy_target(old, {})))
    return rows
