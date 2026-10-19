import os
import re
from functools import lru_cache

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import get_language

# Šířky zmenšenin generovaných příkazem `make_thumbnails`.
THUMB_WIDTHS = (400, 800, 1400)

# Techniky: klíč v DB → český a anglický název, médium a podložka pro
# schema.org. Podložka se uvádí jen tam, kde ji název techniky sám říká.
TECHNIQUES = {
    'oil_canvas': ('olej na plátně', 'oil on canvas', 'oil', 'canvas'),
    'oil_hardboard': ('olej na sololitu', 'oil on hardboard', 'oil', 'hardboard'),
    'watercolour': ('akvarel', 'watercolour', 'watercolour', ''),
    'tempera': ('tempera', 'tempera', 'tempera', ''),
    'gouache': ('kvaš', 'gouache', 'gouache', ''),
    'print': ('grafika', 'print', 'print', ''),
    'mixed': ('kombinovaná technika', 'mixed media', 'mixed media', ''),
    'other': ('jiná', 'other', '', ''),
}
TECHNIQUE_CHOICES = [(key, labels[0]) for key, labels in TECHNIQUES.items()]

# „76×63 cm“ — první číslo je šířka. Ověřeno na všech 38 nečtvercových
# obrazech s rozměrem: orientace fotografie vždy odpovídá pořadí čísel.
_SIZE_RE = re.compile(r'(\d+(?:[.,]\d+)?)\s*[×xX]\s*(\d+(?:[.,]\d+)?)')


@lru_cache(maxsize=2048)
def _thumb_exists(relative_path):
    """Existenci náhledu stačí ověřit jednou za běh procesu."""
    return os.path.exists(os.path.join(settings.MEDIA_ROOT, relative_path))


def _is_en():
    return get_language() == 'en'


class Category(models.Model):
    name = models.CharField('název', max_length=100)
    name_en = models.CharField(
        'název (EN)', max_length=100, blank=True,
        help_text='Nepovinné. Prázdné = zobrazí se český název i v anglické verzi.',
    )
    slug = models.SlugField('slug', unique=True)
    order = models.PositiveIntegerField('pořadí', default=0)

    class Meta:
        verbose_name = 'kategorie'
        verbose_name_plural = 'kategorie'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def display_name(self):
        """Název v aktuálním jazyce, s češtinou jako záložní variantou."""
        if _is_en() and self.name_en:
            return self.name_en
        return self.name

    def get_absolute_url(self):
        return reverse('gallery:category_detail', args=[self.slug])


class Painting(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'K dispozici'),
        ('sold', 'Prodáno'),
        ('not_for_sale', 'Neprodejné'),
    ]

    title = models.CharField(
        'kód obrazu', max_length=200,
        help_text='Kód z autorova katalogu, např. K1. Slouží i jako identifikátor při poptávce.',
    )
    catalog_code = models.CharField(
        'kód v souhrnném katalogu', max_length=20, blank=True,
        help_text='Označení v Katalog.pdf (např. R233) — liší se od kódu na webu. '
                  'Doplňuje ho příkaz apply_catalog_dimensions z ověřených párů.',
    )
    display_title = models.CharField(
        'název obrazu', max_length=200, blank=True,
        help_text='Skutečný název díla, je-li znám, např. „Ráno v Praze“. '
                  'Prázdné = použije se „kategorie + kód“ (Krajinomalba K1). '
                  'Po vyplnění se změní adresa stránky; stará adresa dál funguje.',
    )
    display_title_en = models.CharField(
        'název obrazu (EN)', max_length=200, blank=True,
        help_text='Nepovinné, např. „Morning in Prague“. Prázdné = použije se český název.',
    )
    slug = models.SlugField('slug', max_length=220, blank=True, unique=True)
    category = models.ForeignKey(
        Category, verbose_name='kategorie', on_delete=models.PROTECT, related_name='paintings'
    )
    year = models.PositiveSmallIntegerField(
        'rok vzniku', blank=True, null=True,
        help_text='Jen čtyřmístný rok, např. 1965. Neznámý rok nechte prázdný.',
    )
    year_approx = models.BooleanField(
        'rok je přibližný', default=False,
        help_text='Zaškrtněte, pokud rok není jistý — web zobrazí „cca 1965“.',
    )
    dimensions = models.CharField(
        'rozměry', max_length=100, blank=True,
        help_text='Šířka × výška v centimetrech, např. „76×63 cm“.',
    )
    technique = models.CharField(
        'technika', max_length=30, blank=True, choices=TECHNIQUE_CHOICES,
        help_text='Vyberte, jen pokud je technika jistá.',
    )
    technique_detail = models.CharField(
        'upřesnění techniky', max_length=150, blank=True,
        help_text='Nepovinné, např. „olej a pastel na kartonu“. '
                  'V české verzi se zobrazí místo vybrané techniky.',
    )
    motif = models.CharField(
        'motiv', max_length=200, blank=True,
        help_text='Co obraz zobrazuje, např. „horská krajina v zimě“, „kytice slunečnic“.',
    )
    motif_en = models.CharField(
        'motiv (EN)', max_length=200, blank=True,
        help_text='Nepovinné, např. „mountain landscape in winter“.',
    )
    location_depicted = models.CharField(
        'zobrazené místo', max_length=200, blank=True,
        help_text='Konkrétní místo na obraze, je-li jisté, např. „Krkonoše“, „Ještěd“, '
                  '„Kutná Hora“. Píše se česky, použije se v obou jazycích.',
    )
    is_signed = models.BooleanField(
        'signováno', blank=True, null=True,
        help_text='„Neznámo“ nechte, dokud signaturu na obraze nikdo neověřil.',
    )
    signature_position = models.CharField(
        'umístění signatury', max_length=100, blank=True,
        help_text='Např. „vpravo dole“, „na rubu“.',
    )
    image = models.ImageField('obrázek', upload_to='paintings/%Y/%m/')
    alt_text_cs = models.CharField(
        'alt text', max_length=250, blank=True,
        help_text='Popis obrázku pro nevidomé a vyhledávače. Prázdné = vytvoří se '
                  'automaticky z vyplněných údajů (viz „Automatický alt text“).',
    )
    alt_text_en = models.CharField(
        'alt text (EN)', max_length=250, blank=True,
        help_text='Nepovinné. Prázdné = vytvoří se automaticky v angličtině.',
    )
    description = models.TextField(
        'popis', blank=True,
        help_text='Volný text o obraze. Začátek textu se použije i jako popis pro vyhledávače.',
    )
    description_en = models.TextField(
        'popis (EN)', blank=True,
        help_text='Nepovinné. Prázdné = návštěvník uvidí český text s poznámkou.',
    )
    availability = models.CharField(
        'dostupnost', max_length=20, choices=AVAILABILITY_CHOICES, default='not_for_sale'
    )
    order = models.PositiveIntegerField('pořadí zobrazení', default=0)
    created_at = models.DateTimeField('vytvořeno', auto_now_add=True)
    updated_at = models.DateTimeField('upraveno', auto_now=True)

    class Meta:
        verbose_name = 'obraz'
        verbose_name_plural = 'obrazy'
        ordering = ['order', '-year']

    def __str__(self):
        return self.public_title

    # ------------------------------------------------------------------
    # Údaje pro zobrazení — vždy jen z vyplněných polí, nic se nedomýšlí
    # ------------------------------------------------------------------
    @property
    def public_title(self):
        """Název pro zobrazení — skutečný, nebo záložní „kategorie + kód“."""
        if _is_en() and self.display_title_en:
            return self.display_title_en
        if self.display_title:
            return self.display_title
        return f'{self.category.display_name} {self.title}'

    @property
    def technique_display(self):
        if self.technique_detail and not _is_en():
            return self.technique_detail
        if not self.technique or self.technique == 'other':
            return ''
        labels = TECHNIQUES[self.technique]
        return labels[1] if _is_en() else labels[0]

    @property
    def art_medium(self):
        return TECHNIQUES.get(self.technique, ('', '', '', ''))[2]

    @property
    def artwork_surface(self):
        return TECHNIQUES.get(self.technique, ('', '', '', ''))[3]

    @property
    def year_display(self):
        if not self.year:
            return ''
        if self.year_approx:
            return f'{"c." if _is_en() else "cca"} {self.year}'
        return str(self.year)

    @property
    def motif_display(self):
        if _is_en() and self.motif_en:
            return self.motif_en
        return self.motif

    @property
    def size_cm(self):
        """(šířka, výška) v cm z textového rozměru, nebo None."""
        match = _SIZE_RE.search(self.dimensions or '')
        if not match:
            return None
        return tuple(float(v.replace(',', '.')) for v in match.groups())

    @property
    def dimensions_display(self):
        size = self.size_cm
        if not size:
            return self.dimensions
        return '{:g} × {:g} cm'.format(*size)

    @property
    def is_for_sale(self):
        return self.availability == 'available'

    @property
    def alt_text(self):
        """Ruční alt text, jinak složený jen z vyplněných (ověřených) údajů."""
        manual = self.alt_text_en if _is_en() else self.alt_text_cs
        if manual:
            return manual
        name = self.public_title
        if self.display_title:
            name = f'{name} ({self.category.display_name} {self.title})'
        parts = [f'Oldřich Lajsek – {name}']
        for value in (self.location_depicted, self.technique_display,
                      self.dimensions_display, self.year_display):
            if value:
                parts.append(value)
        return ', '.join(parts)

    # ------------------------------------------------------------------
    # Adresa
    # ------------------------------------------------------------------
    def build_slug(self):
        """Slug z názvu díla; kód obrazu je vždy suffixem kvůli jedinečnosti."""
        base = slugify(self.display_title) if self.display_title else slugify(self.category.name)
        code = slugify(self.title)
        return f'{base}-{code}'.strip('-') if base else code

    def save(self, *args, **kwargs):
        # Slug se drží názvu: po doplnění skutečného názvu se URL přegeneruje.
        # Starou adresu dohledá view painting_detail podle kódu na konci (301).
        self.slug = self.build_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery:painting_detail', args=[self.category.slug, self.slug])

    @property
    def sitemap_images(self):
        """Obrázky stránky pro <image:image> v sitemapě (originál v plném rozlišení)."""
        from core.seo import absolute
        return [absolute(self.image.url)]

    # ------------------------------------------------------------------
    # Zmenšeniny
    # ------------------------------------------------------------------
    def thumb_name(self, width):
        """Cesta náhledu v MEDIA_ROOT: <složka>/thumbs/<soubor>-<šířka>.jpg"""
        base, _ext = os.path.splitext(self.image.name)
        directory, filename = os.path.split(base)
        return f'{directory}/thumbs/{filename}-{width}.jpg'

    def thumb_url(self, width):
        """URL náhledu; když ještě nebyl vygenerován, vrátí originál."""
        name = self.thumb_name(width)
        if _thumb_exists(name):
            return f'{settings.MEDIA_URL}{name}'
        return self.image.url

    @property
    def thumb_small(self):
        return self.thumb_url(400)

    @property
    def thumb_medium(self):
        return self.thumb_url(800)

    @property
    def thumb_large(self):
        return self.thumb_url(1400)

    @property
    def srcset_grid(self):
        """srcset pro mřížku galerie."""
        return f'{self.thumb_url(400)} 400w, {self.thumb_url(800)} 800w'

    @property
    def srcset_detail(self):
        """srcset pro detail obrazu."""
        return (f'{self.thumb_url(800)} 800w, {self.thumb_url(1400)} 1400w')
