"""Doplní obrazům rozměry převzaté z Katalog.pdf.

Pozor na past: kódy na webu a v katalogu si NEODPOVÍDAJÍ. Obraz, který má
na webu kód K1, je v katalogu veden jako R233. Přiřadit rozměry podle
shody kódů by proto zapsalo nesmysly.

Párování proto vzniklo porovnáním samotných reprodukcí (otisk jasu,
barevný histogram a poměr stran) a každý pár byl následně zkontrolován
okem na kontaktním archu. Do data/catalog_dimensions.json jsou zapsané
jen ověřené dvojice — příkaz nic nedopočítává, pouze je aplikuje.

Použití: python manage.py apply_catalog_dimensions [--dry-run]
"""

import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from gallery.models import Painting

DATA_FILE = settings.BASE_DIR / 'data' / 'catalog_dimensions.json'


class Command(BaseCommand):
    help = 'Zapíše ověřené rozměry z katalogu k odpovídajícím obrazům.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Jen vypíše, co by se změnilo, a nic neuloží.',
        )

    def handle(self, *args, **options):
        if not DATA_FILE.exists():
            raise CommandError(f'Chybi soubor s parovanim: {DATA_FILE}')

        with open(DATA_FILE, encoding='utf-8') as fh:
            pairs = json.load(fh)['parovani']

        updated = skipped = missing = 0
        for pair in pairs:
            painting = Painting.objects.filter(title=pair['web']).first()
            if painting is None:
                self.stderr.write(f"chybi obraz s kodem {pair['web']}")
                missing += 1
                continue
            if painting.dimensions == pair['rozmer']:
                skipped += 1
                continue
            self.stdout.write(
                f"  {pair['web']:6} <- katalog {pair['katalog']:7} {pair['rozmer']}"
            )
            if not options['dry_run']:
                painting.dimensions = pair['rozmer']
                painting.save(update_fields=['dimensions'])
            updated += 1

        total = Painting.objects.count()
        with_dimensions = Painting.objects.exclude(dimensions='').count()
        note = ' (zkusebni beh, nic se neulozilo)' if options['dry_run'] else ''
        self.stdout.write(self.style.SUCCESS(
            f'Doplneno: {updated} | jiz melo: {skipped} | nenalezeno: {missing}{note}\n'
            f'Rozmer ma celkem {with_dimensions} z {total} obrazu.'
        ))
