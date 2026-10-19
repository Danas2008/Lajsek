"""Strukturovaná data schema.org (JSON-LD) pro celý web.

Slovníky se skládají v Pythonu a do stránky je vypisuje tag {% jsonld %}
(viz lajsek_tags) — escapování tak řeší json.dumps, ne šablona.

Fakta o autorovi pocházejí výhradně z životopisu na webu (data/wp_content.json).
U obrazů se uvádí jen to, co je v databázi vyplněné; nic se nedopočítává.
"""

from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language

PERSON_ID = '/#person'
WEBSITE_ID = '/#website'


def _abs(path):
    from .seo import absolute
    return absolute(path)


def _en():
    return get_language() == 'en'


def _lang():
    return 'en' if _en() else 'cs'


def person_ref():
    return {'@type': 'Person', '@id': _abs(PERSON_ID), 'name': 'Oldřich Lajsek'}


def person(image_path=None, same_as=()):
    """Plný záznam o autorovi — úvodní stránka a Život."""
    en = _en()
    data = {
        '@context': 'https://schema.org',
        '@type': 'Person',
        '@id': _abs(PERSON_ID),
        'name': 'Oldřich Lajsek',
        'givenName': 'Oldřich',
        'familyName': 'Lajsek',
        'birthDate': '1925-02-08',
        'deathDate': '2001-10-02',
        'birthPlace': {
            '@type': 'Place',
            'name': 'Křesetice',
            'address': {'@type': 'PostalAddress', 'addressLocality': 'Křesetice',
                        'addressCountry': 'CZ'},
        },
        'deathPlace': {
            '@type': 'Place',
            'name': 'Prague' if en else 'Praha',
            'address': {'@type': 'PostalAddress', 'addressLocality': 'Praha',
                        'addressCountry': 'CZ'},
        },
        'nationality': {'@type': 'Country', 'name': 'Czech Republic' if en else 'Česko'},
        'jobTitle': (['Painter', 'Graphic artist', 'Designer', 'Teacher'] if en
                     else ['Malíř', 'Grafik', 'Designér', 'Pedagog']),
        'description': (
            'Czech painter, graphic artist, designer and teacher (1925–2001).' if en
            else 'Český malíř, grafik, designér a pedagog (1925–2001).'
        ),
        'award': (
            'State decoration For Outstanding Work (1985)' if en
            else 'Státní vyznamenání Za vynikající práci (1985)'
        ),
        'alumniOf': {
            '@type': 'CollegeOrUniversity',
            'name': ('Charles University, Faculty of Education' if en
                     else 'Univerzita Karlova, Pedagogická fakulta'),
        },
        'memberOf': [
            {'@type': 'Organization',
             'name': 'Svaz československých výtvarných umělců'},
            {'@type': 'Organization', 'name': 'Směr (Skupina osmi výtvarníků)'},
            {'@type': 'Organization', 'name': 'Spolek Štursa'},
            {'@type': 'Organization', 'name': 'Český svaz bojovníků za svobodu'},
        ],
        'url': _abs(reverse('core:home')),
        'mainEntityOfPage': _abs(reverse('core:life')),
    }
    if image_path:
        data['image'] = _abs(image_path)
    if same_as:
        data['sameAs'] = list(same_as)
    return data


def website():
    """WebSite — na každé stránce, vydavatel podle settings.SITE_PUBLISHER."""
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': _abs(WEBSITE_ID),
        'url': _abs(reverse('core:home')),
        'name': 'Oldřich Lajsek',
        'inLanguage': _lang(),
        'about': person_ref(),
        'publisher': {'@type': 'Person', 'name': settings.SITE_PUBLISHER},
    }


def breadcrumb_list(items):
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': position, 'name': name, 'item': _abs(url)}
            for position, (name, url) in enumerate(items, start=1)
        ],
    }


def _distance(value):
    return {'@type': 'Distance', 'name': f'{value:g} cm'}


def visual_artwork(painting, image_url):
    """VisualArtwork jen z vyplněných údajů; offers bez ceny, je-li na prodej."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'VisualArtwork',
        '@id': _abs(painting.get_absolute_url()) + '#artwork',
        'name': painting.public_title,
        'identifier': painting.title,
        'url': _abs(painting.get_absolute_url()),
        'image': _abs(image_url),
        'creator': person_ref(),
        'artform': 'Print' if painting.technique == 'print' else 'Painting',
        'genre': painting.category.display_name,
        'inLanguage': _lang(),
    }
    if painting.art_medium:
        data['artMedium'] = painting.art_medium
    if painting.artwork_surface:
        data['artworkSurface'] = painting.artwork_surface
    size = painting.size_cm
    if size:
        data['width'] = _distance(size[0])
        data['height'] = _distance(size[1])
    if painting.year:
        data['dateCreated'] = str(painting.year)
    if painting.location_depicted:
        data['contentLocation'] = {'@type': 'Place', 'name': painting.location_depicted}
    if painting.motif_display:
        data['about'] = painting.motif_display
    description = painting.description_en if _en() and painting.description_en else painting.description
    if description:
        data['description'] = description
    if painting.is_for_sale:
        # Bez ceny: validátor schema.org to přijímá, Google pro VisualArtwork
        # rich výsledky nezobrazuje, takže nevzniká chyba „chybí price“.
        data['offers'] = {
            '@type': 'Offer',
            'availability': 'https://schema.org/InStock',
            'url': _abs(painting.get_absolute_url()),
        }
    return data


def exhibition_event(exhibition):
    """ExhibitionEvent — jen pro výstavy se známým rokem a místem."""
    if not (exhibition.year or '').strip().isdigit() or not exhibition.title:
        return None
    return {
        '@context': 'https://schema.org',
        '@type': 'ExhibitionEvent',
        'name': f'{"Exhibition" if _en() else "Výstava"} – {exhibition.title} ({exhibition.year})',
        'startDate': exhibition.year.strip(),
        'eventAttendanceMode': 'https://schema.org/OfflineEventAttendanceMode',
        'location': {
            '@type': 'Place',
            'name': exhibition.title,
            'address': exhibition.title,
        },
        'about': person_ref(),
        'description': exhibition.place,
    }


def faq_page(pairs):
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': question,
                'acceptedAnswer': {'@type': 'Answer', 'text': answer},
            }
            for question, answer in pairs
        ],
    }


def article(headline, description, url, image_url):
    return {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': headline,
        'description': description,
        'url': _abs(url),
        'image': _abs(image_url),
        'inLanguage': _lang(),
        'about': person_ref(),
        'publisher': {'@type': 'Person', 'name': settings.SITE_PUBLISHER},
    }
