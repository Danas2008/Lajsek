"""Vytvoří zmenšené varianty obrazů pro web.

Originály z WordPressu mají kolem 3000 px a 1–2 MB. V galerii se zobrazují
na 300 px, takže se bez náhledů přenáší řádově víc dat, než je potřeba.
Originál zůstává nedotčený — náhledy se ukládají vedle něj do podsložky.

Použití: python manage.py make_thumbnails [--force]
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from gallery.models import THUMB_WIDTHS, Painting


class Command(BaseCommand):
    help = 'Vygeneruje zmenšeniny obrazů (400/800/1400 px) pro rychlé načítání.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Přegeneruje i náhledy, které už existují.',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = skipped = failed = 0
        saved_bytes = 0

        for painting in Painting.objects.select_related('category'):
            source = Path(settings.MEDIA_ROOT) / painting.image.name
            if not source.exists():
                self.stderr.write(f'chybi soubor: {painting.image.name}')
                failed += 1
                continue

            for width in THUMB_WIDTHS:
                target = Path(settings.MEDIA_ROOT) / painting.thumb_name(width)
                if target.exists() and not force:
                    skipped += 1
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with Image.open(source) as im:
                        im = ImageOps.exif_transpose(im)
                        if im.mode not in ('RGB', 'L'):
                            im = im.convert('RGB')
                        if im.width > width:
                            height = round(im.height * width / im.width)
                            im = im.resize((width, height), Image.LANCZOS)
                        im.save(target, 'JPEG', quality=82, optimize=True, progressive=True)
                    created += 1
                    saved_bytes += source.stat().st_size - target.stat().st_size
                except Exception as exc:  # noqa: BLE001 - chceme pokračovat dál
                    self.stderr.write(f'{painting.image.name} @{width}: {exc}')
                    failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Vytvoreno: {created} | preskoceno: {skipped} | chyb: {failed}'
        ))
        if created:
            self.stdout.write(f'Uspora proti originalum: {saved_bytes / 1024 / 1024:.1f} MB')
