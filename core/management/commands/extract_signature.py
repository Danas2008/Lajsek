"""Vytáhne autorův podpis z fotografie do průhledného PNG.

Zdroj (media/pages/Signatura-2.png) není sken podpisu, ale fotografie
podpisu na tmavém podkladu — je celá neprůhledná, s vinětací a zrnem
kamene. Proto se tahy nedají získat prostým prahováním jasu:

1. okraj snímku se ořízne (tvoří tmavý rám),
2. pozadí se odhadne silným rozostřením a odečte — zůstane jen to,
   co je *lokálně* tmavší než okolí, tedy tahy,
3. hysterezní práh: slabé pixely projdou jen tam, kde navazují na
   jistá jádra tahu, což odstraní plošný závoj,
4. zahodí se malé izolované skvrny a dlouhé tenké pruhy po hraně snímku,
5. maska se ztenčí na kostru, najdou se konce tahů a ty, které na sebe
   směřují, se přemostí — doplní se tak tah ztracený v kameni,
6. výsledek se vektorizuje (potrace), takže je ostrý v každé velikosti.

Výstupy: static/img/signature.svg (tmavý tah pro web),
static/img/signature-light.svg (světlý do tmavé lišty adminu),
static/img/favicon.png.

Kroky 5–6 potřebují knihovny navíc (numpy, scikit-image, potracer).
Bez nich příkaz skončí srozumitelnou hláškou; hotové SVG je ve verzi
uložené v repozitáři, takže běh aplikace je nepotřebuje.

Použití: python manage.py extract_signature
"""

import math
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


# --- kostra, přemostění mezer a vektorizace -------------------------------
BRIDGE_MAX_DIST = 64        # nejdelší mezera, kterou ještě spojíme (px)
BRIDGE_MAX_ANGLE = 62       # tahy se musí mířit k sobě do tohoto úhlu
BRIDGE_WIDTH = 7            # šířka doplněného můstku ~ šířka tahu


def _skeleton_neighbours(sk, y, x):
    height, width = sk.shape
    found = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy or dx:
                ny, nx = y + dy, x + dx
                if 0 <= ny < height and 0 <= nx < width and sk[ny, nx]:
                    found.append((ny, nx))
    return found


def _stroke_ends(sk):
    return [(y, x) for y, x in zip(*sk.nonzero())
            if len(_skeleton_neighbours(sk, y, x)) == 1]


def _tangent(sk, end, steps=8):
    """Směr tahu v koncovém bodě — z chůze zpět po kostře."""
    walked = [end]
    previous, current = None, end
    for _ in range(steps):
        options = [n for n in _skeleton_neighbours(sk, *current) if n != previous]
        if not options:
            break
        previous, current = current, options[0]
        walked.append(current)
    if len(walked) < 2:
        return (0.0, 0.0)
    dy = walked[0][0] - walked[-1][0]
    dx = walked[0][1] - walked[-1][1]
    length = math.hypot(dy, dx) or 1
    return (dy / length, dx / length)


def _vectorise(alpha):
    """Doplní přerušené tahy a převede masku na SVG."""
    import numpy as np
    import potrace
    from PIL import ImageDraw
    from skimage.morphology import closing, disk, remove_small_objects, skeletonize

    mask = closing(np.asarray(alpha) >= 100, disk(3))
    mask = remove_small_objects(mask, min_size=180)

    skeleton = skeletonize(mask)
    ends = _stroke_ends(skeleton)
    tangents = {e: _tangent(skeleton, e) for e in ends}

    limit = math.cos(math.radians(BRIDGE_MAX_ANGLE))
    candidates = []
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            a, b = ends[i], ends[j]
            vy, vx = b[0] - a[0], b[1] - a[1]
            distance = math.hypot(vy, vx)
            if distance < 4 or distance > BRIDGE_MAX_DIST:
                continue
            uy, ux = vy / distance, vx / distance
            towards_b = tangents[a][0] * uy + tangents[a][1] * ux
            towards_a = tangents[b][0] * -uy + tangents[b][1] * -ux
            if towards_b > limit and towards_a > limit:
                candidates.append((distance - 26 * (towards_a + towards_b), a, b))

    used, bridges = set(), []
    for _score, a, b in sorted(candidates, key=lambda item: item[0]):
        if a in used or b in used:
            continue
        used.update((a, b))
        bridges.append((a, b))

    drawing = Image.new('L', (mask.shape[1], mask.shape[0]), 0)
    pen = ImageDraw.Draw(drawing)
    for a, b in bridges:
        pen.line([(a[1], a[0]), (b[1], b[0])], fill=255, width=BRIDGE_WIDTH)

    merged = mask | (np.asarray(drawing) > 127)
    smoothed = (Image.fromarray((merged * 255).astype('uint8'))
                .filter(ImageFilter.GaussianBlur(1.4))
                .point(lambda v: 255 if v >= 125 else 0))

    # potracer bere nulové hodnoty jako popředí, proto masku obracíme
    path = potrace.Bitmap(np.asarray(smoothed) <= 127).trace(
        turdsize=12, alphamax=1.2, opttolerance=0.25)

    width, height = smoothed.size
    shapes = []
    for curve in path:
        start = curve.start_point
        parts = [f'M{start.x:.1f} {start.y:.1f}']
        for segment in curve:
            end = segment.end_point
            if segment.is_corner:
                parts.append(f'L{segment.c.x:.1f} {segment.c.y:.1f}'
                             f'L{end.x:.1f} {end.y:.1f}')
            else:
                parts.append(f'C{segment.c1.x:.1f} {segment.c1.y:.1f} '
                             f'{segment.c2.x:.1f} {segment.c2.y:.1f} '
                             f'{end.x:.1f} {end.y:.1f}')
        parts.append('Z')
        shapes.append(''.join(parts))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'fill="#2b2620"><path fill-rule="evenodd" d="{"".join(shapes)}"/></svg>')


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

        try:
            svg = _vectorise(alpha)
        except ImportError as exc:
            raise CommandError(
                'Pro vektorizaci chybi knihovny: pip install numpy scikit-image potracer '
                f'({exc})'
            ) from exc

        img_dir = settings.BASE_DIR / 'static' / 'img'
        img_dir.mkdir(parents=True, exist_ok=True)
        (img_dir / 'signature.svg').write_text(svg, encoding='utf-8')
        (img_dir / 'signature-light.svg').write_text(
            svg.replace('fill="#2b2620"', 'fill="#f7f3ec"'), encoding='utf-8')

        favicon = Image.new('RGBA', (128, 128), (247, 243, 236, 255))
        dark = _tinted(alpha, (43, 38, 32))
        fav_ratio = 108 / dark.width
        small = dark.resize((108, max(1, round(dark.height * fav_ratio))), Image.LANCZOS)
        favicon.paste(small, ((128 - small.width) // 2, (128 - small.height) // 2), small)
        favicon.save(img_dir / 'favicon.png')

        self.stdout.write(self.style.SUCCESS(
            f'Podpis hotov: {alpha.width}x{alpha.height} px, odstraneno skvrn: {removed}'
        ))
