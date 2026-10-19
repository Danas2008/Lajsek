"""Vytvoří zmenšené varianty obrazů pro web.

Originály z WordPressu mají kolem 3000 px a 1–2 MB. V galerii se zobrazují
na 300 px, takže se bez náhledů přenáší řádově víc dat, než je potřeba.
Originál zůstává nedotčený — náhledy se ukládají vedle něj do podsložky:

- <soubor>-400/800/1400.jpg  — pro všechny prohlížeče,
- <soubor>-400/800/1400.webp — menší soubory pro moderní prohlížeče (<picture>),
- <soubor>-og.jpg            — 1200×630 pro sdílení (Facebook, WhatsApp…).
  Obraz se nikdy neořezává: vloží se celý doprostřed papírového podkladu.

Použití: python manage.py make_thumbnails [--force]
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from gallery.models import OG_SIZE, THUMB_WIDTHS, Painting

PAPER = (247, 243, 236)     # --paper ze style.css
OG_MARGIN = 40


def _open_rgb(source):
    im = Image.open(source)
    im = ImageOps.exif_transpose(im)
    if im.mode not in ('RGB', 'L'):
        im = im.convert('RGB')
    return im


def _resized(im, width):
    if im.width <= width:
        return im
    height = round(im.height * width / im.width)
    return im.resize((width, height), Image.LANCZOS)


def _og_image(im):
    canvas = Image.new('RGB', OG_SIZE, PAPER)
    box = (OG_SIZE[0] - 2 * OG_MARGIN, OG_SIZE[1] - 2 * OG_MARGIN)
    art = im.convert('RGB').copy()
    art.thumbnail(box, Image.LANCZOS)
    canvas.paste(art, ((OG_SIZE[0] - art.width) // 2, (OG_SIZE[1] - art.height) // 2))
    return canvas


class Command(BaseCommand):
    help = 'Vygeneruje zmenšeniny obrazů (400/800/1400 px, JPEG + WebP) a obrázek pro sdílení.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Přegeneruje i náhledy, které už existují.',
        )

    def handle(self, *args, **options):
        force = options['force']
        created = skipped = failed = 0
        media = Path(settings.MEDIA_ROOT)

        for painting in Painting.objects.select_related('category'):
            source = media / painting.image.name
            if not source.exists():
                self.stderr.write(f'chybi soubor: {painting.image.name}')
                failed += 1
                continue

            jobs = []
            for width in THUMB_WIDTHS:
                jobs.append((painting.thumb_name(width), 'JPEG', width))
                jobs.append((painting.thumb_name(width, 'webp'), 'WEBP', width))
            jobs.append((painting.og_name(), 'OG', None))

            pending = [job for job in jobs if force or not (media / job[0]).exists()]
            skipped += len(jobs) - len(pending)
            if not pending:
                continue

            try:
                with _open_rgb(source) as im:
                    for name, kind, width in pending:
                        target = media / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if kind == 'OG':
                            _og_image(im).save(target, 'JPEG', quality=84, optimize=True,
                                               progressive=True)
                        elif kind == 'WEBP':
                            _resized(im, width).save(target, 'WEBP', quality=80, method=6)
                        else:
                            _resized(im, width).save(target, 'JPEG', quality=82, optimize=True,
                                                     progressive=True)
                        created += 1
            except Exception as exc:  # noqa: BLE001 - chceme pokračovat dál
                self.stderr.write(f'{painting.image.name}: {exc}')
                failed += 1

        self.stdout.write(self.style.SUCCESS(
            f'Vytvoreno: {created} | preskoceno: {skipped} | chyb: {failed}'
        ))
