from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),

    path('o-autorovi/', views.biography, name='biography'),
    path('o-autorovi/zivot/', views.life, name='life'),
    path('o-autorovi/dilo/', views.work, name='work'),
    path('o-autorovi/katalog/', views.catalog, name='catalog'),

    path('vystavy/', views.exhibitions, name='exhibitions'),
    path('napsali-o-nem/', views.press, name='press'),
    path('odkazy/', views.links, name='links'),
    path('kontakt/', views.contact, name='contact'),

    # Původní adresy ze starší verze webu — trvalé přesměrování, ať se
    # nerozbijí už rozeslané odkazy ani indexace.
    path('zivotopis/', RedirectView.as_view(pattern_name='core:biography', permanent=True)),
    path('zivotopis/zivot/', RedirectView.as_view(pattern_name='core:life', permanent=True)),
    path('zivotopis/dilo/', RedirectView.as_view(pattern_name='core:work', permanent=True)),
    path('zivotopis/katalog/', RedirectView.as_view(pattern_name='core:catalog', permanent=True)),
]
