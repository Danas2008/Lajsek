from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from core import content

from .models import Category, Painting


def _list_context(request, active_category=None):
    paintings = Painting.objects.select_related('category').all()
    if active_category:
        paintings = paintings.filter(category=active_category)
        title = f'{active_category.display_name} | Oldřich Lajsek'
        description = _(
            'Obrazy z kategorie %(category)s v díle českého malíře Oldřicha Lajska.'
        ) % {'category': active_category.display_name}
    else:
        title = _('Nabídka obrazů') + ' | Oldřich Lajsek'
        description = _(
            'Přehled obrazů Oldřicha Lajska — krajinomalba, abstrakce, '
            'realismus a květinová zátiší.'
        )
    return {
        'meta_title': title,
        'meta_description': description,
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


def painting_detail(request, category_slug, slug):
    painting = get_object_or_404(
        Painting.objects.select_related('category'),
        slug=slug,
        category__slug=category_slug,
    )
    related = (
        Painting.objects.select_related('category')
        .filter(category=painting.category)
        .exclude(pk=painting.pk)[:4]
    )
    context = {
        'meta_title': f'{painting.public_title} | Oldřich Lajsek',
        'meta_description': painting.description[:160] if painting.description else _(
            'Obraz %(title)s od českého malíře Oldřicha Lajska (1925–2001).'
        ) % {'title': painting.public_title},
        'painting': painting,
        'related': related,
        'og_image_url': painting.thumb_large,
    }
    return render(request, 'gallery/painting_detail.html', context)


def painting_redirect(request, pk):
    """Trvalé přesměrování ze starých číselných adres na nové slugy."""
    painting = get_object_or_404(Painting.objects.select_related('category'), pk=pk)
    return redirect(painting.get_absolute_url(), permanent=True)
