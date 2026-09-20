"""
Django settings for lajsek project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-ui((5_4w___p^upb!&-6t9rr-zzhw!=@an5@9id1ahlszljh_w',
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()
]


# Application definition

INSTALLED_APPS = [
    # Musí být před django.contrib.admin, jinak se šablony nepřepíšou.
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    'core',
    'gallery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lajsek.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.i18n',
                'core.context_processors.language_links',
                'gallery.context_processors.nav_categories',
            ],
        },
    },
]

WSGI_APPLICATION = 'lajsek.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'cs'

LANGUAGES = [
    ('cs', 'Čeština'),
    ('en', 'English'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

TIME_ZONE = 'Europe/Prague'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploaded painting images)

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site settings used across templates / SEO
SITE_NAME = 'Oldřich Lajsek'
SITE_DOMAIN = os.environ.get('DJANGO_SITE_DOMAIN', 'lajsek.cz')


# ---------------------------------------------------------------------------
# Admin (Jazzmin)
# Správu vede netechnický uživatel, proto je menu seřazené podle toho,
# jak s obsahem reálně pracuje: obrazy → kategorie → výstavy → tisk → zprávy.
# ---------------------------------------------------------------------------

JAZZMIN_SETTINGS = {
    'site_title': 'Lajsek — správa',
    'site_header': 'Oldřich Lajsek',
    'site_brand': 'Lajsek Admin',
    'welcome_sign': 'Správa díla Oldřicha Lajska',
    'copyright': 'Rodina Lajskova',

    # Autorův podpis; v tmavé liště se převrací do bílé (viz admin.css).
    'site_logo': 'img/admin-logo.png',
    'site_logo_classes': 'img-size-50',
    'site_icon': 'img/favicon.png',
    'login_logo': 'img/admin-logo.png',

    'order_with_respect_to': [
        'gallery',
        'gallery.painting',
        'gallery.category',
        'core',
        'core.exhibition',
        'core.pressmention',
        'core.externallink',
        'core.contactmessage',
        'auth',
    ],

    'icons': {
        'gallery.painting': 'fas fa-palette',
        'gallery.category': 'fas fa-tags',
        'core.exhibition': 'fas fa-landmark',
        'core.pressmention': 'fas fa-newspaper',
        'core.externallink': 'fas fa-link',
        'core.contactmessage': 'fas fa-envelope',
        'auth.user': 'fas fa-user',
        'auth.group': 'fas fa-users',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',

    # Odkaz zpět na veřejný web přímo z horní lišty.
    'topmenu_links': [
        {'name': 'Zobrazit web', 'url': '/', 'new_window': True},
        {'model': 'auth.user'},
    ],

    'show_ui_builder': False,
    'related_modal_active': True,
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'auth.user': 'collapsible',
        'auth.group': 'vertical_tabs',
    },
    'custom_css': 'css/admin.css',
    'language_chooser': False,
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    # Jazzmin 3 řídí světlý/tmavý režim přes data-bs-theme.
    'default_theme_mode': 'light',
    'navbar': 'navbar-dark',
    'accent': 'accent-warning',
    'brand_colour': 'navbar-dark',
    'sidebar': 'sidebar-dark-warning',
    'sidebar_nav_flat_style': True,
    'no_navbar_border': True,
    'body_small_text': False,
    'navbar_small_text': False,
    'sidebar_nav_small_text': False,
    'actions_sticky_top': True,
}

# Dlouhá relace: správce edituje desítky obrazů v jednom sezení a nesmí ho
# admin odhlásit uprostřed práce.
SESSION_COOKIE_AGE = 60 * 60 * 12          # 12 hodin
SESSION_SAVE_EVERY_REQUEST = True          # každá akce platnost prodlouží
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7         # týden, ať nevyprší formulář
