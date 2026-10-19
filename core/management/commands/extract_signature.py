"""Převede sken autorova podpisu do vektorového SVG s průhledným pozadím.

Zdroj (media/pages/Černý podpis O. Lajsek.png) je čistý černý podpis
na bílém podkladu, takže stačí:

1. převést na odstíny šedi a ořezat na kresbu s malým okrajem,
2. zmenšit na pracovní výšku (2× výška SVG — zachová charakter tahu,
   ale zahladí zrno skenu),
3. prahovat jas a výsledek vektorizovat (potrace), takže je ostrý
   v každé velikosti.

Výstupy: static/img/signature.svg (tmavý tah pro web),
static/img/signature-light.svg (světlý do tmavé lišty adminu),
static/img/favicon.png.

Vektorizace potřebuje knihovny navíc (numpy, potracer). Bez nich příkaz
skončí srozumitelnou hláškou; hotové SVG je ve verzi uložené
v repozitáři, takže běh aplikace je nepotřebuje.

Použití: python manage.py extract_signature
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageFilter, ImageOps

SOURCE = 'pages/Černý podpis O. Lajsek.png'
INK_THRESHOLD = 128         # jas pod touto hodnotou je inkoust
PAD = 0.03                  # okraj kolem kresby (podíl výšky)
OUT_HEIGHT = 186            # 3× zobrazovaná výška (62 px) kvůli retině
TRACE_SCALE = 2             # trasuje se v 2× rozlišení výstupu


def _vectorise(ink, view_height):
    """Převede masku inkoustu (255 = tah) na SVG o dané výšce viewBoxu."""
    import numpy as np
    import potrace

    # potracer bere nulové hodnoty jako popředí, proto masku obracíme
    path = potrace.Bitmap(np.asarray(ink) < 128).trace(
        turdsize=8, alphamax=1.0, opttolerance=0.2)

    k = view_height / ink.height
    width = round(ink.width * k)
    shapes = []
    for curve in path:
        start = curve.start_point
        parts = [f'M{start.x * k:.1f} {start.y * k:.1f}']
        for segment in curve:
            end = segment.end_point
            if segment.is_corner:
                parts.append(f'L{segment.c.x * k:.1f} {segment.c.y * k:.1f}'
                             f'L{end.x * k:.1f} {end.y * k:.1f}')
            else:
                parts.append(f'C{segment.c1.x * k:.1f} {segment.c1.y * k:.1f} '
                             f'{segment.c2.x * k:.1f} {segment.c2.y * k:.1f} '
                             f'{end.x * k:.1f} {end.y * k:.1f}')
        parts.append('Z')
        shapes.append(''.join(parts))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {view_height}" '
           f'fill="#2b2620"><path fill-rule="evenodd" d="{"".join(shapes)}"/></svg>')
    return svg, width


class Command(BaseCommand):
    help = 'Vytvoří průhledné varianty autorova podpisu ze skenu.'

    def handle(self, *args, **options):
        source_path = settings.MEDIA_ROOT / SOURCE
        if not source_path.exists():
            raise CommandError(f'Chybí zdrojový sken: {source_path}')

        gray = Image.open(source_path).convert('L')
        ink = ImageOps.invert(gray).point(lambda v: 255 if v > 255 - INK_THRESHOLD else 0)

        bbox = ink.getbbox()
        if not bbox:
            raise CommandError('Ve skenu nebyla nalezena žádná kresba.')
        pad = round((bbox[3] - bbox[1]) * PAD)
        ink = ink.crop((
            max(0, bbox[0] - pad), max(0, bbox[1] - pad),
            min(ink.width, bbox[2] + pad), min(ink.height, bbox[3] + pad),
        ))

        # zmenšení přes šedou (vyhlazení hran), pak znovu prahovat
        trace_height = OUT_HEIGHT * TRACE_SCALE
        trace_width = round(ink.width * trace_height / ink.height)
        ink = (ink.resize((trace_width, trace_height), Image.LANCZOS)
               .filter(ImageFilter.GaussianBlur(0.8))
               .point(lambda v: 255 if v >= 128 else 0))

        try:
            svg, width = _vectorise(ink, OUT_HEIGHT)
        except ImportError as exc:
            raise CommandError(
                f'Pro vektorizaci chybi knihovny: pip install numpy potracer ({exc})'
            ) from exc

        img_dir = settings.BASE_DIR / 'static' / 'img'
        img_dir.mkdir(parents=True, exist_ok=True)
        (img_dir / 'signature.svg').write_text(svg, encoding='utf-8')
        (img_dir / 'signature-light.svg').write_text(
            svg.replace('fill="#2b2620"', 'fill="#f7f3ec"'), encoding='utf-8')

        favicon = Image.new('RGBA', (128, 128), (247, 243, 236, 255))
        dark = Image.new('RGBA', ink.size, (43, 38, 32, 0))
        dark.putalpha(ink)
        small = dark.resize((116, max(1, round(dark.height * 116 / dark.width))), Image.LANCZOS)
        favicon.paste(small, ((128 - small.width) // 2, (128 - small.height) // 2), small)
        favicon.save(img_dir / 'favicon.png')

        self.stdout.write(self.style.SUCCESS(
            f'Podpis hotov: {width}x{OUT_HEIGHT} (viewBox)'
        ))
