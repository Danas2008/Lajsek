from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from gallery.models import Category, Painting
from gallery.views import painting_description


class PaintingDisplayTests(TestCase):
    """Zobrazované údaje vznikají jen z vyplněných polí."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name='Krajinomalba', name_en='Landscape painting', slug='krajinomalba',
        )

    def _painting(self, **fields):
        defaults = {'title': 'K1', 'category': self.category, 'image': 'paintings/test/k1.jpg'}
        return Painting.objects.create(**{**defaults, **fields})

    def test_alt_text_with_code_only(self):
        painting = self._painting()
        self.assertEqual(painting.alt_text, 'Oldřich Lajsek – Krajinomalba K1')
        with translation.override('en'):
            self.assertEqual(painting.alt_text, 'Oldřich Lajsek – Landscape painting K1')

    def test_alt_text_with_all_fields(self):
        painting = self._painting(
            display_title='Ještěd', location_depicted='Ještěd', technique='oil_canvas',
            dimensions='76×63 cm', year=1965, year_approx=True,
        )
        self.assertEqual(
            painting.alt_text,
            'Oldřich Lajsek – Ještěd (Krajinomalba K1), Ještěd, olej na plátně, 76 × 63 cm, cca 1965',
        )

    def test_manual_alt_text_wins(self):
        painting = self._painting(alt_text_cs='Ruční popis', alt_text_en='Manual')
        self.assertEqual(painting.alt_text, 'Ruční popis')
        with translation.override('en'):
            self.assertEqual(painting.alt_text, 'Manual')

    def test_size_parsing(self):
        self.assertEqual(self._painting(dimensions='76×63 cm').size_cm, (76.0, 63.0))
        self.assertEqual(self._painting(title='K2', dimensions='32,5 x 45 cm').size_cm, (32.5, 45.0))
        self.assertIsNone(self._painting(title='K3', dimensions='').size_cm)

    def test_other_technique_is_not_displayed(self):
        self.assertEqual(self._painting(technique='other').technique_display, '')
        painting = self._painting(title='K2', technique='other', technique_detail='olej na kartonu')
        self.assertEqual(painting.technique_display, 'olej na kartonu')

    def test_description_fits_and_keeps_code(self):
        painting = self._painting(
            display_title='Velmi dlouhý název obrazu z cesty do Jugoslávie',
            technique='oil_hardboard', dimensions='120×90 cm', year=1970, year_approx=True,
            availability='available',
        )
        for language in ('cs', 'en'):
            with translation.override(language):
                text = painting_description(painting)
                self.assertLessEqual(len(text), 160, text)
                self.assertIn('K1', text)


class PaintingUrlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.landscape = Category.objects.create(name='Krajinomalba', slug='krajinomalba')
        cls.abstract = Category.objects.create(name='Abstrakce', slug='abstrakce')
        cls.painting = Painting.objects.create(
            title='K1', category=cls.landscape, image='paintings/test/k1.jpg',
            availability='available',
        )

    def test_adding_title_keeps_old_url_working(self):
        old_url = self.painting.get_absolute_url()
        self.painting.display_title = 'Ještěd'
        self.painting.save()
        new_url = self.painting.get_absolute_url()
        self.assertNotEqual(old_url, new_url)

        response = self.client.get(old_url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], new_url)

    def test_wrong_category_redirects(self):
        url = reverse('gallery:painting_detail', args=['abstrakce', self.painting.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], self.painting.get_absolute_url())

    def test_unknown_code_is_404(self):
        url = reverse('gallery:painting_detail', args=['krajinomalba', 'krajinomalba-k999'])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_cta_only_for_available(self):
        html = self.client.get(self.painting.get_absolute_url()).content.decode()
        self.assertIn('?obraz=K1', html)
        self.painting.availability = 'sold'
        self.painting.save()
        html = self.client.get(self.painting.get_absolute_url()).content.decode()
        self.assertNotIn('?obraz=K1', html)


class SimilarSizeTests(TestCase):
    def test_similar_size_block(self):
        category = Category.objects.create(name='Realismus', slug='realismus')
        other = Category.objects.create(name='Abstrakce', slug='abstrakce')
        base = Painting.objects.create(title='R1', category=category, image='a.jpg',
                                       dimensions='76×63 cm')
        Painting.objects.create(title='A1', category=other, image='b.jpg', dimensions='80×60 cm')
        Painting.objects.create(title='A2', category=other, image='c.jpg', dimensions='30×20 cm')

        html = self.client.get(base.get_absolute_url()).content.decode()
        self.assertIn('Podobné rozměry', html)
        self.assertIn('kód A1', html)
        self.assertNotIn('kód A2', html)
