from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import get_language


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
        if get_language() == 'en' and self.name_en:
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
    display_title = models.CharField(
        'název obrazu', max_length=200, blank=True,
        help_text='Skutečný název díla, je-li znám. Prázdné = použije se „kategorie + kód“.',
    )
    slug = models.SlugField('slug', max_length=220, blank=True, unique=True)
    category = models.ForeignKey(
        Category, verbose_name='kategorie', on_delete=models.PROTECT, related_name='paintings'
    )
    year = models.CharField('rok vzniku', max_length=20, blank=True)
    dimensions = models.CharField('rozměry', max_length=100, blank=True)
    technique = models.CharField('technika', max_length=150, blank=True)
    image = models.ImageField('obrázek', upload_to='paintings/%Y/%m/')
    image_alt = models.CharField('alt text obrázku', max_length=200)
    description = models.TextField('popis', blank=True)
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

    @property
    def public_title(self):
        """Název pro zobrazení — skutečný, nebo záložní „kategorie + kód“."""
        if self.display_title:
            return self.display_title
        return f'{self.category.display_name} {self.title}'

    def build_slug(self):
        """Slug z názvu díla; kód obrazu je vždy suffixem kvůli jedinečnosti."""
        base = slugify(self.display_title) if self.display_title else slugify(self.category.name)
        code = slugify(self.title)
        return f'{base}-{code}'.strip('-') if base else code

    def save(self, *args, **kwargs):
        # Slug se drží názvu: po doplnění skutečného názvu se URL přegeneruje.
        self.slug = self.build_slug()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('gallery:painting_detail', args=[self.category.slug, self.slug])
