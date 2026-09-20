from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from . import content
from .forms import ContactForm
from .models import Exhibition, ExternalLink, PressMention

SITE = 'Oldřich Lajsek'


def home(request):
    hero_images = content.page_images('uvod')
    context = {
        'meta_title': _('Oldřich Lajsek — český malíř (1925–2001)'),
        'meta_description': _(
            'Prezentace celoživotního díla českého malíře Oldřicha Lajska '
            '(1925–2001). Krajinomalba, abstrakce, realismus a květinová zátiší.'
        ),
        'hero_image': hero_images[0] if hero_images else None,
        'motto': PressMention.objects.filter(kind='quote').first(),
        'intro': content.paragraphs('nabidka'),
        'is_home': True,
    }
    return render(request, 'core/home.html', context)


def biography(request):
    """Rozcestník O autorovi (Život / Dílo / Katalog)."""
    context = {
        'meta_title': _('O autorovi') + f' | {SITE}',
        'meta_description': _('Život, dílo a katalog malíře Oldřicha Lajska.'),
    }
    return render(request, 'core/biography.html', context)


def life(request):
    context = {
        'meta_title': _('Život') + f' | {SITE}',
        'meta_description': _(
            'Životopis českého malíře Oldřicha Lajska (1925–2001) — '
            'od rodných Křesetic po pražskou Ořechovku.'
        ),
        'paragraphs': content.paragraphs('zivot'),
        'untranslated': content.is_untranslated('zivot'),
        'images': content.page_images('zivot'),
    }
    return render(request, 'core/life.html', context)


def work(request):
    context = {
        'meta_title': _('Dílo') + f' | {SITE}',
        'meta_description': _(
            'Tvorba, žánry a umělecký rukopis malíře Oldřicha Lajska.'
        ),
        'paragraphs': content.paragraphs('dilo'),
        'untranslated': content.is_untranslated('dilo'),
        'images': content.page_images('dilo'),
    }
    return render(request, 'core/work.html', context)


def catalog(request):
    context = {
        'meta_title': _('Katalog') + f' | {SITE}',
        'meta_description': _('Katalog děl Oldřicha Lajska ke stažení ve formátu PDF.'),
    }
    return render(request, 'core/catalog.html', context)


def exhibitions(request):
    context = {
        'meta_title': _('Výstavy') + f' | {SITE}',
        'meta_description': _(
            'Přehled samostatných i společných výstav Oldřicha Lajska '
            'v Česku i v zahraničí.'
        ),
        'exhibitions': Exhibition.objects.order_by('place', 'order'),
    }
    return render(request, 'core/exhibitions.html', context)


def press(request):
    context = {
        'meta_title': _('Napsali o něm') + f' | {SITE}',
        'meta_description': _(
            'Citáty výtvarných teoretiků a bibliografie k dílu Oldřicha Lajska.'
        ),
        'quotes': PressMention.objects.filter(kind='quote'),
        'publications': PressMention.objects.filter(kind='publication'),
    }
    return render(request, 'core/press.html', context)


def links(request):
    context = {
        'meta_title': _('Odkazy') + f' | {SITE}',
        'meta_description': _(
            'Galerie, katalogy a databáze, v nichž je dílo Oldřicha Lajska zastoupeno.'
        ),
        'links': ExternalLink.objects.all(),
    }
    return render(request, 'core/links.html', context)


def contact(request):
    initial = {}
    painting_title = request.GET.get('obraz')
    if painting_title:
        initial['message'] = _(
            'Dobrý den,\nmám zájem o obraz s kódem „%(code)s“. '
            'Prosím o zaslání bližších informací.'
        ) % {'code': painting_title}

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Děkujeme za zprávu, ozveme se vám co nejdříve.'))
            return redirect(reverse('core:contact'))
    else:
        form = ContactForm(initial=initial)

    context = {
        'meta_title': _('Kontakt') + f' | {SITE}',
        'meta_description': _(
            'Kontakt pro zájemce o dílo Oldřicha Lajska — syn malíře JUDr. Jan Lajsek.'
        ),
        'form': form,
        'paragraphs': content.paragraphs('kontakt'),
        'untranslated': content.is_untranslated('kontakt'),
    }
    return render(request, 'core/contact.html', context)
