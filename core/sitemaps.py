from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from gallery.models import Category, Painting


class StaticViewSitemap(Sitemap):
    """Statické stránky, v české i anglické verzi."""

    changefreq = 'monthly'
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return [
            'core:home',
            'core:biography',
            'core:life',
            'core:work',
            'core:catalog',
            'core:exhibitions',
            'core:press',
            'core:links',
            'core:contact',
            'gallery:painting_list',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'core:home' else 0.6


class CategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return Category.objects.all()


class PaintingSitemap(Sitemap):
    changefreq = 'yearly'
    priority = 0.8
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return Painting.objects.select_related('category').all()

    def lastmod(self, obj):
        return obj.updated_at


SITEMAPS = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'paintings': PaintingSitemap,
}
