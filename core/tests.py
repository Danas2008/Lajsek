import json
import re

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from core.articles import ARTICLES
from core.models import ContactMessage, Exhibition, ExternalLink, PressMention
from gallery.models import Category, Painting

JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def _public_paths():
    """Všechny veřejné stránky (bez prefixu jazyka)."""
    paths = [
        reverse('core:home'),
        reverse('core:biography'),
        reverse('core:life'),
        reverse('core:work'),
        reverse('core:catalog'),
        reverse('core:exhibitions'),
        reverse('core:press'),
        reverse('core:links'),
        reverse('core:contact'),
        reverse('gallery:painting_list'),
        reverse('gallery:category_detail', args=['krajinomalba']),
        reverse('gallery:painting_detail', args=['krajinomalba', 'krajinomalba-k1']),
        reverse('gallery:painting_detail', args=['krajinomalba', 'krajinomalba-k2']),
    ]
    paths += [reverse(f'core:article-{slug}') for slug in ARTICLES]
    return paths


class SeoFixtureMixin:
    @classmethod
    def setUpTestData(cls):
        cls.landscape = Category.objects.create(
            name='Krajinomalba', name_en='Landscape painting', slug='krajinomalba', order=0,
            intro='První odstavec.\n\nDruhý odstavec.',
        )
        Category.objects.create(name='Abstrakce', name_en='Abstraction', slug='abstrakce', order=1)
        cls.k1 = Painting.objects.create(
            title='K1', category=cls.landscape, image='paintings/test/k1.jpg',
            dimensions='76×63 cm', catalog_code='R233', availability='available',
        )
        cls.k2 = Painting.objects.create(
            title='K2', category=cls.landscape, image='paintings/test/k2.jpg',
            dimensions='80×60 cm', technique='oil_canvas', year=1965, year_approx=True,
            availability='sold',
        )
        Exhibition.objects.create(title='Kutná Hora', place='Účast na výstavách', year='1956')
        Exhibition.objects.create(title='Lodž', place='Zahraničí', year='')
        PressMention.objects.create(kind='quote', source='Autor citátu', text='Citát.')
        ExternalLink.objects.create(
            title='Wikipedie', url='https://cs.wikipedia.org/wiki/Old%C5%99ich_Lajsek',
            is_profile=True,
        )
        ExternalLink.objects.create(title='Katalog knihovny', url='https://katalog.example.cz/')


class PublicPagesSeoTests(SeoFixtureMixin, TestCase):
    """Každá veřejná stránka v CS i EN má základní SEO prvky."""

    def _check(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200, path)
        html = response.content.decode()

        self.assertEqual(len(re.findall(r'<h1[\s>]', html)), 1, f'{path}: počet <h1>')

        title = re.search(r'<title>(.*?)</title>', html, re.S)
        self.assertTrue(title and title.group(1).strip(), f'{path}: <title>')

        description = re.search(r'<meta name="description" content="([^"]*)"', html)
        self.assertTrue(description and description.group(1).strip(), f'{path}: description')
        self.assertLessEqual(len(description.group(1)), 200, path)  # HTML entity rozšíří délku

        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        self.assertTrue(canonical, f'{path}: canonical')
        self.assertTrue(canonical.group(1).endswith(path), f'{path}: canonical na sebe')

        self.assertIn('hreflang="cs"', html, path)
        self.assertIn('hreflang="x-default"', html, path)
        self.assertIn('property="og:image"', html, path)

        blocks = JSONLD_RE.findall(html)
        self.assertTrue(blocks, f'{path}: JSON-LD')
        for block in blocks:
            data = json.loads(block)
            self.assertEqual(data['@context'], 'https://schema.org', path)
        return html

    def test_czech_pages(self):
        for path in _public_paths():
            with self.subTest(path=path):
                html = self._check(path)
                self.assertIn('<html lang="cs">', html)

    def test_english_pages(self):
        for path in _public_paths():
            path = '/en' + path
            with self.subTest(path=path):
                html = self._check(path)
                self.assertIn('<html lang="en">', html)

    def test_untranslated_page_does_not_offer_english_alternate(self):
        # Texty Života zatím nemají EN verzi (data/wp_content.json → texts_en).
        html = self.client.get(reverse('core:life')).content.decode()
        self.assertNotIn('hreflang="en"', html)
        html = self.client.get(reverse('core:exhibitions')).content.decode()
        self.assertIn('hreflang="en"', html)

    def test_canonical_ignores_query_string(self):
        html = self.client.get(reverse('core:contact') + '?obraz=K1').content.decode()
        self.assertIn('rel="canonical" href="https://lajsek.cz/kontakt/"', html)


class StructuredDataTests(SeoFixtureMixin, TestCase):
    def _blocks(self, path):
        html = self.client.get(path).content.decode()
        return [json.loads(block) for block in JSONLD_RE.findall(html)]

    def _schema(self, path):
        """JSON-LD stránky podle @type (poslední blok daného typu)."""
        return {block['@type']: block for block in self._blocks(path)}

    def test_home_person(self):
        person = self._schema(reverse('core:home'))['Person']
        self.assertEqual(person['birthDate'], '1925-02-08')
        self.assertEqual(person['deathDate'], '2001-10-02')
        self.assertEqual(person['birthPlace']['name'], 'Křesetice')
        # sameAs jen z odkazů označených jako profil autora
        self.assertEqual(person['sameAs'], ['https://cs.wikipedia.org/wiki/Old%C5%99ich_Lajsek'])

    def test_artwork_only_verified_fields(self):
        artwork = self._schema(self.k1.get_absolute_url())['VisualArtwork']
        self.assertEqual(artwork['width'], {'@type': 'Distance', 'name': '76 cm'})
        self.assertEqual(artwork['height'], {'@type': 'Distance', 'name': '63 cm'})
        self.assertEqual(artwork['offers']['availability'], 'https://schema.org/InStock')
        self.assertNotIn('price', artwork['offers'])
        for missing in ('artMedium', 'dateCreated', 'artworkSurface', 'description'):
            self.assertNotIn(missing, artwork)

    def test_sold_artwork_has_medium_and_no_offer(self):
        artwork = self._schema(self.k2.get_absolute_url())['VisualArtwork']
        self.assertEqual(artwork['artMedium'], 'oil')
        self.assertEqual(artwork['artworkSurface'], 'canvas')
        self.assertEqual(artwork['dateCreated'], '1965')
        self.assertNotIn('offers', artwork)

    def test_breadcrumbs(self):
        crumbs = self._schema(self.k1.get_absolute_url())['BreadcrumbList']['itemListElement']
        self.assertEqual([item['position'] for item in crumbs], [1, 2, 3, 4])
        self.assertEqual(crumbs[-1]['item'], 'https://lajsek.cz' + self.k1.get_absolute_url())

    def test_exhibition_events_only_with_year(self):
        events = [item for item in self._blocks(reverse('core:exhibitions'))
                  if item['@type'] == 'ExhibitionEvent']
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['startDate'], '1956')

    def test_faq_excludes_unverified_answers(self):
        faq = self._schema(reverse('core:article-jak-koupit'))['FAQPage']
        answers = [item['acceptedAnswer']['text'] for item in faq['mainEntity']]
        self.assertTrue(answers)
        self.assertFalse(any('TODO' in answer for answer in answers))

    def test_jsonld_cannot_break_out_of_script(self):
        self.k1.description = '</script><script>alert(1)</script>'
        self.k1.save()
        html = self.client.get(self.k1.get_absolute_url()).content.decode()
        self.assertNotIn('<script>alert(1)', html)


class TodoVisibilityTests(SeoFixtureMixin, TestCase):
    def test_todo_hidden_from_public_and_shown_to_staff(self):
        url = reverse('core:article-jak-koupit')
        self.assertNotIn('TODO(rodina)', self.client.get(url).content.decode())

        staff = get_user_model().objects.create_user('spravce', password='x', is_staff=True)
        self.client.force_login(staff)
        self.assertIn('TODO(rodina)', self.client.get(url).content.decode())


class TechnicalSeoTests(SeoFixtureMixin, TestCase):
    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('Disallow: /admin/', body)
        self.assertIn('Sitemap: https://lajsek.cz/sitemap.xml', body)

    def test_sitemap_has_images_and_alternates(self):
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('xmlns:image=', body)
        self.assertIn('<image:loc>https://lajsek.cz/media/paintings/test/k1.jpg</image:loc>', body)
        self.assertIn('<loc>https://lajsek.cz/jak-koupit/</loc>', body)
        self.assertIn('hreflang="en" href="https://lajsek.cz/en/obrazy/"', body)
        # Nepřeložený Život je v sitemapě jen česky
        self.assertNotIn('<loc>https://lajsek.cz/en/o-autorovi/zivot/</loc>', body)

    @override_settings(DEBUG=False)
    def test_custom_404(self):
        response = self.client.get('/tato-stranka-neexistuje/')
        self.assertEqual(response.status_code, 404)
        html = response.content.decode()
        self.assertIn('noindex', html)
        self.assertIn(self.landscape.get_absolute_url(), html)

    def test_lowercase_redirect(self):
        response = self.client.get('/Obrazy/Krajinomalba/?x=1')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/obrazy/krajinomalba/?x=1')

    def test_wordpress_redirects(self):
        cases = {
            '/?page_id=62': reverse('core:life'),
            '/?p=13': reverse('gallery:painting_list'),
            '/?page_id=131': self.landscape.get_absolute_url(),
            '/?attachment_id=125': self.k1.get_absolute_url(),
            '/?attachment_id=161': reverse('gallery:category_detail', args=['abstrakce']),
            '/wp-content/uploads/2016/09/IMG_9761-150x150.jpg': '/media/paintings/test/k1.jpg',
            '/wp-content/uploads/2016/09/Katalog.pdf': '/media/pages/Katalog.pdf',
        }
        for old, new in cases.items():
            with self.subTest(old=old):
                response = self.client.get(old)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response['Location'], new)

    def test_wordpress_feed_is_gone(self):
        self.assertEqual(self.client.get('/?feed=rss2').status_code, 410)

    def test_unknown_query_on_home_is_not_redirected(self):
        self.assertEqual(self.client.get('/?utm_source=x').status_code, 200)


class ContactConversionTests(SeoFixtureMixin, TestCase):
    def test_prefilled_code_and_thank_you_url(self):
        html = self.client.get(reverse('core:contact') + '?obraz=K1').content.decode()
        self.assertIn('„K1“', html)

        response = self.client.post(reverse('core:contact'), {
            'name': 'Jana', 'email': 'jana@example.cz', 'message': 'Mám zájem o K1.',
        })
        self.assertRedirects(response, reverse('core:contact_thanks'))
        self.assertEqual(ContactMessage.objects.count(), 1)

        html = self.client.get(reverse('core:contact_thanks')).content.decode()
        self.assertIn('noindex', html)
