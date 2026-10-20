from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static as static_url
from django.urls import include, path
from django.views.generic import RedirectView

from core.sitemaps import SITEMAPS
from core.views import robots_txt

# Mimo i18n_patterns — nemají jazykovou variantu.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS},
         name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
    # Prohlížeče a čtečky RSS hledají ikonu i bez <link> přímo v kořeni webu.
    path('favicon.ico', RedirectView.as_view(url=static_url('img/favicon.ico'), permanent=True)),
]

# Čeština zůstává bez prefixu, angličtina běží na /en/...
urlpatterns += i18n_patterns(
    path('obrazy/', include('gallery.urls')),
    path('', include('core.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
