"""Sitemapa s jazykovými variantami (hreflang) a obrázky obrazů.

Doména a protokol se berou ze SITE_URL, ne z požadavku — sitemapa tak
vždy obsahuje kanonické https adresy. Anglická varianta stránky se uvádí,
jen když má stránka anglický obsah (stejné pravidlo jako hreflang v hlavičce).
"""

from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.db.models import Max
from django.urls import reverse

from core import content
from core.models import PressMention
from gallery.models import Category, Painting


class CanonicalSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True

    @property
    def protocol(self):
        return urlsplit(settings.SITE_URL).scheme or 'https'

    def get_domain(self, site=None):
        return urlsplit(settings.SITE_URL).netloc


def _press_translated():
    return not PressMention.objects.filter(text_en='').exists()


class StaticViewSitemap(CanonicalSitemap):
    """Statické stránky; u nepřeložených jen česká verze."""

    changefreq = 'monthly'

    # url name → funkce „má stránka anglický obsah?“
    PAGES = {
        'core:home': None,
        'core:biography': None,
        'core:life': lambda: content.has_translation('zivot'),
        'core:work': lambda: content.has_translation('dilo'),
        'core:catalog': None,
        'core:exhibitions': None,
        'core:press': _press_translated,
        'core:links': None,
        'core:contact': lambda: content.has_translation('kontakt'),
        'gallery:painting_list': None,
    }

    def items(self):
        return list(self.PAGES)

    def location(self, item):
        return reverse(item)

    def get_languages_for_item(self, item):
        check = self.PAGES[item]
        if check is None or check():
            return super().get_languages_for_item(item)
        return [settings.LANGUAGE_CODE]

    def priority(self, item):
        if item == 'core:home':
            return 1.0
        if item == 'gallery:painting_list':
            return 0.9
        return 0.6


class CategorySitemap(CanonicalSitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Category.objects.annotate(last_change=Max('paintings__updated_at'))

    def lastmod(self, obj):
        return obj.last_change


class PaintingSitemap(CanonicalSitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Painting.objects.select_related('category').all()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'paintings': PaintingSitemap,
}
