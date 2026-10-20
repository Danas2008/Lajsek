"""Jednorázové vygenerování sady faviconů z autorova podpisu.

Monogram „O. L“ se vyřízne přímo z static/img/signature.svg (začátek
podpisu), takže ikona zůstane věrná originálu i po jeho případné výměně.

Vytvoří ve static/img/:
    favicon.svg           — 32×32, světlá i tmavá varianta (prefers-color-scheme)
    favicon.ico           — 16 + 32 px
    apple-touch-icon.png  — 180×180, neprůhledné pozadí (iOS si rohy zakulatí sám)
    icon-192.png, icon-512.png — pro site.webmanifest; obsah drží v bezpečné
                            zóně, takže se dají použít i jako „maskable“

Skript nepatří do produkce a nemá závislosti v requirements.txt.
Spouští se v dočasném virtuálním prostředí z kořene projektu:

    python -m venv /tmp/favenv
    /tmp/favenv/bin/pip install resvg-py pillow      (Windows: favenv\\Scripts\\pip)
    /tmp/favenv/bin/python scripts/make_favicons.py
"""

import io
import re
from pathlib import Path

import resvg_py
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / 'static' / 'img'

# Barvy ze static/css/style.css
PAPER = '#f7f3ec'   # --paper
INK = '#2b2620'     # --ink

NUM = re.compile(r'-?\d+(?:\.\d+)?')


def monogram_path():
    """Části podpisu „O“, „.“ a „L“ — podtahy začínající v levé části (x < 200 z 518).

    Horní kudrlinka L sahá dál doprava, proto se vybírá podle začátku, ne konce.
    """
    svg = (IMG / 'signature.svg').read_text(encoding='utf-8')
    d = re.search(r' d="([^"]+)"', svg).group(1)
    parts = [part for part in re.split(r'(?=M)', d) if part.strip()]
    keep, boxes = [], []
    for part in parts:
        nums = [float(n) for n in NUM.findall(part)]
        xs, ys = nums[0::2], nums[1::2]
        if min(xs) < 200:
            keep.append(part)
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
           max(b[2] for b in boxes), max(b[3] for b in boxes))
    return ''.join(keep), box


def icon_svg(inner, rx, dark_mode=False, thicken=1.6):
    """SVG 32×32: monogram široký `inner` jednotek na zaobleném (rx) podkladu.

    `thicken` zesílí tah (v jednotkách mřížky 32): v 16 px je podpis jinak
    moc tenký, na velkých dlaždicích by ale ztratil charakter.
    """
    d, (x0, y0, x1, y1) = monogram_path()
    width, height = x1 - x0, y1 - y0
    scale = inner / max(width, height)
    tx = (32 - width * scale) / 2 - x0 * scale
    ty = (32 - height * scale) / 2 - y0 * scale
    stroke = thicken / scale
    style = ''
    if dark_mode:
        style = (
            '\n  <style>'
            f'.bg{{fill:{PAPER}}}.ink{{fill:{INK};stroke:{INK}}}'
            '@media (prefers-color-scheme:dark)'
            f'{{.bg{{fill:{INK}}}.ink{{fill:{PAPER};stroke:{PAPER}}}}}'
            '</style>'
        )
        bg_attr, ink_attr = 'class="bg"', 'class="ink"'
    else:
        bg_attr, ink_attr = f'fill="{PAPER}"', f'fill="{INK}" stroke="{INK}"'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{style}\n'
        f'  <rect width="32" height="32" rx="{rx}" {bg_attr}/>\n'
        f'  <path {ink_attr} transform="translate({tx:.2f} {ty:.2f}) scale({scale:.4f})" '
        f'stroke-width="{stroke:.2f}" stroke-linejoin="round" fill-rule="evenodd" d="{d}"/>\n'
        '</svg>\n'
    )


def render(svg, size):
    png = resvg_py.svg_to_bytes(svg_string=svg, width=size, height=size)
    return Image.open(io.BytesIO(bytes(png))).convert('RGBA')


def main():
    favicon = icon_svg(inner=28.5, rx=6)
    (IMG / 'favicon.svg').write_text(icon_svg(inner=28.5, rx=6, dark_mode=True), encoding='utf-8')

    # ICO: každá velikost vykreslená zvlášť (ostřejší než zmenšení z 32 px)
    small, large = render(favicon, 16), render(favicon, 32)
    large.save(IMG / 'favicon.ico', format='ICO', sizes=[(16, 16), (32, 32)],
               append_images=[small])

    # Dlaždice: celý čtverec neprůhledný, monogram menší kvůli ořezu do kruhu/čtverce
    render(icon_svg(inner=24, rx=0, thicken=0.4), 180).convert('RGB').save(IMG / 'apple-touch-icon.png')
    for size in (192, 512):
        render(icon_svg(inner=22, rx=0, thicken=0.3), size).convert('RGB').save(IMG / f'icon-{size}.png')

    for name in ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png'):
        print(f'{name:22} {(IMG / name).stat().st_size:>7} B')


if __name__ == '__main__':
    main()
