from django.urls import path

from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.painting_list, name='painting_list'),
    # Legacy /obrazy/<id>/ — musí předcházet slug patternu (číslice projdou i slugem).
    path('<int:pk>/', views.painting_redirect, name='painting_by_pk'),
    path('<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:slug>/', views.painting_detail, name='painting_detail'),
]
