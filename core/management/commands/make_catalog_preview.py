"""Vyrenderuje náhled katalogu a spočítá fakta, která se o něm uvádějí na webu.

Zdrojem je media/pages/Katalog.pdf převzatý ze starého webu. Náhled se
bere ze strany s reprodukcemi, ne z titulní — ta má ve zdrojovém PDF
zrcadlově převrácený duplikát nadpisu a na webu by vypadala jako chyba.

Čísla (počet dvoustran a počet děl s uvedeným rozměrem) se ukládají do
data/wp_content.json, aby web neuváděl žádný údaj, který by nebyl
odečtený přímo ze zdroje.

Použití: python manage.py make_catalog_preview
"""

import json
import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

PDF = 'pages/Katalog.pdf'
PREVIEW = 'pages/catalog-preview.jpg'
PREVIEW_PAGE = 1            # druhá dvoustrana — první strana s reprodukcemi
LEFT_HALF = 0.492           # dvoustrana se ořízne na levou stranu
MAX_WIDTH = 1200
CODE_RE = re.compile(r'\b([A-Z]{1,2}\d{1,3})\s*/\s*Rozm')


class Command(BaseCommand):
    help = 'Vytvoří náhled katalogu a doplní jeho údaje do data/wp_content.json.'

    def handle(self, *args, **options):
        try:
            import pymupdf
        except ImportError as exc:
            raise CommandError(
                'Chybi knihovna pymupdf — nainstaluj: pip install pymupdf'
            ) from exc

        source = settings.MEDIA_ROOT / PDF
        if not source.exists():
            raise CommandError(f'Chybi zdrojove PDF: {source}')

        document = pymupdf.open(source)

        page = document[PREVIEW_PAGE]
        pixmap = page.get_pixmap(dpi=200)
        image = Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)
        image = image.crop((0, 0, int(image.width * LEFT_HALF), image.height))
        image.thumbnail((MAX_WIDTH, MAX_WIDTH), Image.LANCZOS)

        target = settings.MEDIA_ROOT / PREVIEW
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target, 'JPEG', quality=86, optimize=True, progressive=True)

        codes = set()
        for pdf_page in document:
            codes.update(CODE_RE.findall(pdf_page.get_text()))

        data_file = settings.BASE_DIR / 'data' / 'wp_content.json'
        with open(data_file, encoding='utf-8') as fh:
            data = json.load(fh)
        data['catalog'] = {
            'spreads': document.page_count,
            'works_with_dimensions': len(codes),
            'preview': PREVIEW,
        }
        with open(data_file, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1)

        self.stdout.write(self.style.SUCCESS(
            f'Nahled: {image.width}x{image.height} px | dvoustran: {document.page_count} | '
            f'del s rozmerem: {len(codes)}'
        ))
