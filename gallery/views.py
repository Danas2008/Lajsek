from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext as _

from core import content, schema
from core.seo import DESCRIPTION_LIMIT, PageMeta, absolute, clip, fit_title

from .models import Category, Painting

SUFFIX_ARTIST = ' – Oldřich Lajsek'


def _gallery_crumb():
    return (_('Obrazy'), reverse('gallery:painting_list'))


def _list_context(request, active_category=None):
    paintings = Painting.objects.select_related('category').all()
    if active_category:
        paintings = paintings.filter(category=active_category)
        name = active_category.display_name
        count = paintings.count()
        seo = PageMeta(
            title=fit_title(
                _('%(category)s – obrazy Oldřicha Lajska') % {'category': name},
                _(' | originály k prodeji'),
            ),
            description=_(
                '%(category)s Oldřicha Lajska (1925–2001): %(count)s originálních obrazů '
                'z pozůstalosti autora. Prohlédněte si nabídku a pošlete nezávaznou '
                'poptávku s kódem díla.'
            ) % {'category': name, 'count': count},
            breadcrumbs=[_gallery_crumb(), (name, active_category.get_absolute_url())],
        )
    else:
        seo = PageMeta(
            title=fit_title(_('Obrazy Oldřicha Lajska'), _(' – originály z pozůstalosti k prodeji')),
            description=_(
                'Originální obrazy Oldřicha Lajska z pozůstalosti: krajinomalba, abstrakce, '
                'realismus a květinová zátiší. Vyberte si dílo a pošlete poptávku s kódem.'
            ),
            breadcrumbs=[_gallery_crumb()],
        )
    return {
        'seo': seo,
        'categories': Category.objects.all(),
        'paintings': paintings,
        'active_category': active_category,
        # Na webu je jen část díla — katalog eviduje řádově víc prací.
        'shown_count': Painting.objects.count(),
        'catalog': content.catalog(),
    }


def painting_list(request):
    """Výpis všech obrazů. ?kategorie=<slug> zůstává kvůli starším odkazům."""
    category_slug = request.GET.get('kategorie')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        return redirect(category.get_absolute_url(), permanent=True)
    return render(request, 'gallery/painting_list.html', _list_context(request))


def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    return render(request, 'gallery/painting_list.html', _list_context(request, category))


def _painting_by_old_slug(slug):
    """Obraz podle kódu na konci slugu — slug se mění po doplnění názvu."""
    code = slug.rsplit('-', 1)[-1]
    matches = [
        painting for painting in Painting.objects.select_related('category')
        if slugify(painting.title) == code
    ]
    return matches[0] if len(matches) == 1 else None


def _similar_size(painting, exclude, limit=4, tolerance=0.25):
    """Obrazy s podobnou plochou (±25 %) — pro zájemce, kteří hledají obraz na konkrétní stěnu."""
    size = painting.size_cm
    if not size:
        return []
    area = size[0] * size[1]
    candidates = []
    for other in (Painting.objects.select_related('category')
                  .exclude(dimensions='').exclude(pk__in=exclude)):
        other_size = other.size_cm
        if not other_size:
            continue
        ratio = other_size[0] * other_size[1] / area
        if abs(ratio - 1) <= tolerance:
            candidates.append((abs(ratio - 1), other.is_for_sale is False, other))
    candidates.sort(key=lambda item: (item[1], item[0]))
    return [other for _diff, _sold, other in candidates[:limit]]


def painting_description(painting):
    """Meta description obrazu — jen z vyplněných údajů, vždy s kódem a dostupností.

    Když se plná verze nevejde do 160 znaků, zkrátí se úvodní věta a pak
    se postupně vynechá rok a technika; kód a dostupnost zůstávají vždy.
    """
    title = {'title': painting.public_title}
    openings = [
        _('%(title)s – originální obraz českého malíře Oldřicha Lajska (1925–2001) '
          'z pozůstalosti autora.') % title,
        _('%(title)s – originální obraz Oldřicha Lajska (1925–2001) z pozůstalosti.') % title,
    ]
    if painting.availability == 'available':
        closing = _('Kód %(code)s, k prodeji – pošlete nezávaznou poptávku.')
    elif painting.availability == 'sold':
        closing = _('Kód %(code)s, prodáno.')
    else:
        closing = _('Kód %(code)s, není na prodej.')
    closing = closing % {'code': painting.title}

    detail_sets = [
        (painting.technique_display, painting.dimensions_display, painting.year_display),
        (painting.technique_display, painting.dimensions_display),
        (painting.dimensions_display,),
    ]
    candidates = []
    for details in detail_sets:
        joined = ', '.join(value for value in details if value)
        middle = f' {joined[:1].upper()}{joined[1:]}.' if joined else ''
        candidates += [f'{opening}{middle} {closing}' for opening in openings]
    for text in candidates:
        if len(text) <= DESCRIPTION_LIMIT:
            return text
    # Extrémně dlouhý název: zkrátí se název, kód a dostupnost zůstanou.
    tail = f' – Oldřich Lajsek. {closing}'
    return clip(painting.public_title, DESCRIPTION_LIMIT - len(tail)) + tail


def painting_detail(request, category_slug, slug):
    painting = Painting.objects.select_related('category').filter(slug=slug).first()
    if painting is None:
        # Stará adresa (před doplněním názvu nebo změnou kategorie) → 301.
        painting = _painting_by_old_slug(slug)
        if painting is None:
            raise Http404
        return redirect(painting.get_absolute_url(), permanent=True)
    if painting.category.slug != category_slug:
        return redirect(painting.get_absolute_url(), permanent=True)

    related = (
        Painting.objects.select_related('category')
        .filter(category=painting.category)
        .exclude(pk=painting.pk)[:4]
    )

    similar_size = _similar_size(painting, exclude=[painting.pk, *(p.pk for p in related)])

    og_image = painting.og_image
    seo = PageMeta(
        title=fit_title(
            painting.public_title, SUFFIX_ARTIST, _(' | originál z pozůstalosti'),
        ),
        description=painting_description(painting),
        image={**og_image, 'url': absolute(og_image['url']), 'alt': painting.alt_text},
        breadcrumbs=[
            _gallery_crumb(),
            (painting.category.display_name, painting.category.get_absolute_url()),
            (painting.public_title, painting.get_absolute_url()),
        ],
        schema=[schema.visual_artwork(painting, painting.thumb_large)],
        og_type='article',
    )
    context = {
        'seo': seo,
        'painting': painting,
        'related': related,
        'similar_size': similar_size,
    }
    return render(request, 'gallery/painting_detail.html', context)


def painting_redirect(request, pk):
    """Trvalé přesměrování ze starých číselných adres na nové slugy."""
    painting = get_object_or_404(Painting.objects.select_related('category'), pk=pk)
    return redirect(painting.get_absolute_url(), permanent=True)
