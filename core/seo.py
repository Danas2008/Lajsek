"""Centrální SEO údaje stránky: titulek, popis, obrázek, drobečky, JSON-LD.

Každý view vrací do kontextu ``seo`` (objekt PageMeta) a base.html z něj
vykreslí <title>, meta description, canonical, hreflang, Open Graph,
viditelnou drobečkovou navigaci i strukturovaná data. Šablona tak nemá
vlastní logiku a stránka bez ``seo`` (např. 404) dostane rozumné výchozí
hodnoty.
"""

from dataclasses import dataclass, field

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.encoding import iri_to_uri
from django.utils.translation import gettext as _

from . import schema

TITLE_LIMIT = 60
DESCRIPTION_LIMIT = 160

DEFAULT_IMAGE = {
    'path': 'img/og-default.jpg',
    'width': 1200,
    'height': 630,
}


def absolute(path):
    """Absolutní URL na kanonické doméně (SITE_URL), ne podle hlavičky Host."""
    if path.startswith(('http://', 'https://')):
        return iri_to_uri(path)
    return settings.SITE_URL.rstrip('/') + iri_to_uri(path)


def fit_title(main, *suffixes):
    """Klíčové slovo na začátek; přípony se přidávají, dokud se vejdou do limitu."""
    title = main
    for suffix in suffixes:
        if len(title) + len(suffix) <= TITLE_LIMIT:
            title += suffix
    return title


def clip(text, limit=DESCRIPTION_LIMIT):
    """Zkrátí text na hranici slova, aby ho vyhledávač neuřízl uprostřed."""
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit - 1].rsplit(' ', 1)[0].rstrip(',;:–-')
    return cut + '…'


@dataclass
class PageMeta:
    title: str
    description: str
    image: dict = None            # {'url', 'width', 'height', 'alt'}
    breadcrumbs: list = field(default_factory=list)   # [(název, url)], bez úvodu
    schema: list = field(default_factory=list)        # slovníky JSON-LD
    og_type: str = 'website'
    # False = obsah stránky v EN zatím chybí (zobrazí se čeština). Anglická
    # verze pak není nabízena přes hreflang ani v sitemapě.
    translated: bool = True

    def __post_init__(self):
        self.description = clip(self.description)
        if self.image is None:
            self.image = default_image()
        crumbs = self.breadcrumb_items
        if crumbs:
            self.schema = [*self.schema, schema.breadcrumb_list(crumbs)]
        self.schema = [schema.website(), *self.schema]

    @property
    def breadcrumb_items(self):
        """Drobečky včetně úvodní stránky; na úvodní stránce žádné."""
        if not self.breadcrumbs:
            return []
        return [(_('Úvod'), reverse('core:home')), *self.breadcrumbs]


def default_image():
    return {
        'url': absolute(static(DEFAULT_IMAGE['path'])),
        'width': DEFAULT_IMAGE['width'],
        'height': DEFAULT_IMAGE['height'],
        'alt': _('Portrét Oldřicha Lajska'),
    }
