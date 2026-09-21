"""Vytáhne autorův podpis z fotografie do průhledného PNG.

Zdroj (media/pages/Signatura-2.png) není sken podpisu, ale fotografie
podpisu na tmavém podkladu — je celá neprůhledná, s vinětací a zrnem
kamene. Proto se tahy nedají získat prostým prahováním jasu:

1. okraj snímku se ořízne (tvoří tmavý rám),
2. pozadí se odhadne silným rozostřením a odečte — zůstane jen to,
   co je *lokálně* tmavší než okolí, tedy tahy,
3. hysterezní práh: slabé pixely projdou jen tam, kde navazují na
   jistá jádra tahu, což odstraní plošný závoj,
4. zahodí se malé izolované skvrny a dlouhé tenké pruhy po hraně snímku.

Výstupy: static/img/signature.png (tmavý tah pro web),
static/img/admin-logo.png (světlý pro tmavou lištu adminu),
static/img/favicon.png.

Použití: python manage.py extract_signature
"""

from collections import deque

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from PIL import Image, ImageChops, ImageFilter

SOURCE = 'pages/Signatura-2.png'
INSET = (5, 7, 5, 7)        # ořez rámu fotografie: vlevo, nahoře, vpravo, dole
SCALE = 4                   # předzvětšení, ať mají tahy dost pixelů
BLUR = 24                   # poloměr odhadu pozadí
WEAK_PCT, STRONG_PCT = 66, 90
GROW = 21                   # okolí jader, kam smí slabé pixely
OUT_HEIGHT = 186            # 3× zobrazovaná výška (62 px) kvůli retině


def _percentile(img, p):
    hist = img.histogram()
    total = sum(hist)
    cumulative = 0
    for value, count in enumerate(hist):
        cumulative += count
        if cumulative >= total * p / 100:
            return value
    return 255


def _alpha_from_photo(src):
    img = src.resize((src.width * SCALE, src.height * SCALE), Image.LANCZOS)
    background = img.filter(ImageFilter.GaussianBlur(BLUR))
    detail = ImageChops.subtract(background, img).filter(ImageFilter.MedianFilter(5))

    weak = _percentile(detail, WEAK_PCT)
    strong = _percentile(detail, STRONG_PCT)
    top = max(detail.getextrema()[1], weak + 4)
    curve = [
        0 if v <= weak else min(255, int(((v - weak) / (top - weak)) ** 0.7 * 255 * 1.25))
        for v in range(256)
    ]
    alpha = detail.point(curve)

    seeds = detail.point(lambda v: 255 if v >= strong else 0)
    region = seeds.filter(ImageFilter.MaxFilter(GROW)).filter(ImageFilter.GaussianBlur(2))
    region = region.point(lambda v: 255 if v > 40 else 0)
    alpha = ImageChops.multiply(alpha, region)

    alpha = alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return alpha.filter(ImageFilter.GaussianBlur(1.3))


def _drop_noise(alpha, threshold=45):
    """Odstraní malé skvrny a ploché pruhy; podpis je velká souvislá kresba."""
    width, height = alpha.size
    px = alpha.load()
    min_area = int(width * height * 0.0012)
    seen = bytearray(width * height)
    keep = Image.new('L', (width, height), 0)
    keep_px = keep.load()
    removed = 0

    for start_y in range(height):
        for start_x in range(width):
            if seen[start_y * width + start_x] or px[start_x, start_y] < threshold:
                continue
            queue = deque([(start_x, start_y)])
            seen[start_y * width + start_x] = 1
            cells = []
            min_x = max_x = start_x
            min_y = max_y = start_y
            while queue:
                x, y = queue.popleft()
                cells.append((x, y))
                min_x, max_x = min(min_x, x), max(max_x, x)
                min_y, max_y = min(min_y, y), max(max_y, y)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        idx = ny * width + nx
                        if not seen[idx] and px[nx, ny] >= threshold:
                            seen[idx] = 1
                            queue.append((nx, ny))
            flat_streak = (max_y - min_y + 1) <= 10 and (max_x - min_x + 1) > width * 0.18
            if len(cells) >= min_area and not flat_streak:
                for x, y in cells:
                    keep_px[x, y] = 255
            else:
                removed += 1

    keep = keep.filter(ImageFilter.MaxFilter(5))
    return ImageChops.multiply(alpha, keep), removed


def _tinted(alpha, rgb):
    image = Image.new('RGBA', alpha.size, rgb + (0,))
    image.putalpha(alpha)
    return image


class Command(BaseCommand):
    help = 'Vytvoří průhledné varianty autorova podpisu z fotografie.'

    def handle(self, *args, **options):
        source_path = settings.MEDIA_ROOT / SOURCE
        if not source_path.exists():
            raise CommandError(f'Chybí zdrojová fotografie: {source_path}')

        raw = Image.open(source_path).convert('L')
        src = raw.crop((INSET[0], INSET[1], raw.width - INSET[2], raw.height - INSET[3]))

        alpha = _alpha_from_photo(src)
        alpha, removed = _drop_noise(alpha)

        bbox = alpha.point(lambda v: 255 if v > 55 else 0).getbbox()
        if bbox:
            pad = 10
            alpha = alpha.crop((
                max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(alpha.width, bbox[2] + pad), min(alpha.height, bbox[3] + pad),
            ))

        ratio = OUT_HEIGHT / alpha.height
        alpha = alpha.resize((max(1, round(alpha.width * ratio)), OUT_HEIGHT), Image.LANCZOS)

        img_dir = settings.BASE_DIR / 'static' / 'img'
        img_dir.mkdir(parents=True, exist_ok=True)

        _tinted(alpha, (43, 38, 32)).save(img_dir / 'signature.png')
        logo_ratio = 40 / alpha.height
        light = _tinted(alpha, (247, 243, 236)).resize(
            (max(1, round(alpha.width * logo_ratio)), 40), Image.LANCZOS)
        light.save(img_dir / 'admin-logo.png')

        favicon = Image.new('RGBA', (128, 128), (247, 243, 236, 255))
        dark = _tinted(alpha, (43, 38, 32))
        fav_ratio = 108 / dark.width
        small = dark.resize((108, max(1, round(dark.height * fav_ratio))), Image.LANCZOS)
        favicon.paste(small, ((128 - small.width) // 2, (128 - small.height) // 2), small)
        favicon.save(img_dir / 'favicon.png')

        self.stdout.write(self.style.SUCCESS(
            f'Podpis hotov: {alpha.width}x{alpha.height} px, '
            f'odstraneno skvrn: {removed}'
        ))
