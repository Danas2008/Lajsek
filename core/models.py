from django.db import models


class ContactMessage(models.Model):
    name = models.CharField('jméno', max_length=150)
    email = models.EmailField('e-mail')
    message = models.TextField('zpráva')
    created_at = models.DateTimeField('odesláno', auto_now_add=True)
    is_read = models.BooleanField('přečteno', default=False)

    class Meta:
        verbose_name = 'kontaktní zpráva'
        verbose_name_plural = 'kontaktní zprávy'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.created_at:%d.%m.%Y})'


class Exhibition(models.Model):
    title = models.CharField('název', max_length=200)
    place = models.CharField('místo', max_length=200)
    year = models.CharField('rok', max_length=20)
    description = models.TextField('popis', blank=True)
    description_en = models.TextField(
        'popis (EN)', blank=True,
        help_text='Nepovinné. Prázdné = zobrazí se český text.',
    )
    order = models.PositiveIntegerField('pořadí', default=0)

    class Meta:
        verbose_name = 'výstava'
        verbose_name_plural = 'výstavy'
        ordering = ['-year', 'order']

    def __str__(self):
        return f'{self.title} ({self.year})'


class PressMention(models.Model):
    KIND_CHOICES = [
        ('quote', 'Citát'),
        ('publication', 'Publikace'),
    ]

    kind = models.CharField('druh', max_length=20, choices=KIND_CHOICES, default='quote')
    source = models.CharField('zdroj', max_length=200)
    text = models.TextField('text')
    text_en = models.TextField(
        'text (EN)', blank=True,
        help_text='Nepovinné. Citáty a bibliografie se nepřekládají strojově — '
                  'prázdné pole znamená, že se zobrazí český originál.',
    )
    link = models.URLField('odkaz', blank=True)
    date = models.DateField('datum', blank=True, null=True)
    order = models.PositiveIntegerField('pořadí', default=0)

    class Meta:
        verbose_name = 'zmínka v tisku'
        verbose_name_plural = 'napsali o něm'
        ordering = ['kind', 'order']

    def __str__(self):
        return f'{self.source}'


class ExternalLink(models.Model):
    ICON_CHOICES = [
        ('library', 'Knihovna / muzeum'),
        ('wiki', 'Encyklopedie'),
        ('catalog', 'Katalog / databáze děl'),
        ('gallery', 'Galerie'),
        ('generic', 'Neutrální (typ z názvu nevyplývá)'),
    ]

    title = models.CharField('název', max_length=200)
    icon = models.CharField(
        'ikona', max_length=20, choices=ICON_CHOICES, default='generic',
        help_text='Typ odhadnutý z názvu odkazu. Když si nejste jistí, '
                  'nechte neutrální — nic se tím netvrdí o obsahu odkazu.',
    )
    url = models.URLField('odkaz')
    description = models.CharField('popis', max_length=300, blank=True)
    order = models.PositiveIntegerField('pořadí', default=0)

    class Meta:
        verbose_name = 'odkaz'
        verbose_name_plural = 'odkazy'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
