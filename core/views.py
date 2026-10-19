from itertools import groupby
from operator import attrgetter

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from . import content, schema
from .forms import ContactForm
from .models import Exhibition, ExternalLink, PressMention
from .seo import PageMeta, fit_title

SUFFIX = ' – Oldřich Lajsek'


def _person():
    """Plný záznam Person včetně portrétu a profilů (sameAs) z adminu."""
    portrait = content.portrait_path()
    return schema.person(
        image_path=f'{settings.MEDIA_URL}{portrait}' if portrait else None,
        same_as=ExternalLink.objects.filter(is_profile=True).values_list('url', flat=True),
    )


def _about_crumbs(*extra):
    return [(_('O autorovi'), reverse('core:biography')), *extra]


def home(request):
    hero_images = content.page_images('uvod')
    seo = PageMeta(
        title=_('Oldřich Lajsek (1925–2001) – český malíř | obrazy z pozůstalosti'),
        description=_(
            'Oldřich Lajsek (1925–2001), český malíř, grafik a pedagog. Krajinomalba, '
            'abstrakce, realismus a květinová zátiší – originální obrazy z pozůstalosti.'
        ),
        schema=[_person()],
    )
    context = {
        'seo': seo,
        'hero_image': hero_images[0] if hero_images else None,
        'motto': PressMention.objects.filter(kind='quote').first(),
        'intro': content.paragraphs('nabidka'),
        'is_home': True,
    }
    return render(request, 'core/home.html', context)


def biography(request):
    """Rozcestník O autorovi (Život / Dílo / Katalog)."""
    seo = PageMeta(
        title=fit_title(_('O autorovi'), SUFFIX, _(', malíř, grafik a pedagog')),
        description=_(
            'Oldřich Lajsek (1925–2001) – český malíř, grafik, designér a pedagog. '
            'Životopis od Křesetic u Kutné Hory po Prahu, přehled díla a katalog obrazů.'
        ),
        breadcrumbs=[(_('O autorovi'), reverse('core:biography'))],
    )
    return render(request, 'core/biography.html', {'seo': seo})


def life(request):
    seo = PageMeta(
        title=fit_title(_('Životopis'), SUFFIX, ' (1925–2001)', _(', český malíř')),
        description=_(
            'Životopis malíře Oldřicha Lajska (1925–2001): dětství v Kutné Hoře, odboj v organizaci '
            'Pěst, studia u Karla Lidického, SUPŠ v Praze a skupina Směr.'
        ),
        breadcrumbs=_about_crumbs((_('Život'), reverse('core:life'))),
        schema=[_person()],
        translated=content.has_translation('zivot'),
        og_type='profile',
    )
    context = {
        'seo': seo,
        'sections': content.biography_sections(),
        'untranslated': content.is_untranslated('zivot'),
        'images': content.page_images('zivot'),
    }
    return render(request, 'core/life.html', context)


def work(request):
    seo = PageMeta(
        title=fit_title(_('Dílo Oldřicha Lajska'), _(' – krajinomalba, abstrakce, zátiší')),
        description=_(
            'Tvorba Oldřicha Lajska: zhruba 3000 maleb a grafik, krajinomalba Kutnohorska, '
            'Polabí a Českého středohoří, abstrakce 60. let, realismus a květinová zátiší.'
        ),
        breadcrumbs=_about_crumbs((_('Dílo'), reverse('core:work'))),
        translated=content.has_translation('dilo'),
    )
    context = {
        'seo': seo,
        'paragraphs': content.paragraphs('dilo'),
        'untranslated': content.is_untranslated('dilo'),
        'images': content.page_images('dilo'),
    }
    return render(request, 'core/work.html', context)


def catalog(request):
    data = content.catalog()
    total = data.get('works_with_dimensions')
    seo = PageMeta(
        title=fit_title(_('Katalog děl'), SUFFIX, _(' | obrazy s rozměry')),
        description=(_(
            'Souhrnný katalog díla malíře Oldřicha Lajska: %(total)s obrazů řazených po '
            'kategoriích, u každého kód díla a rozměr. Ke stažení zdarma ve formátu PDF.'
        ) % {'total': total}) if total else _(
            'Souhrnný katalog díla Oldřicha Lajska s kódy děl a rozměry, '
            'řazený po kategoriích. Ke stažení zdarma ve formátu PDF.'
        ),
        breadcrumbs=_about_crumbs((_('Katalog'), reverse('core:catalog'))),
    )
    return render(request, 'core/catalog.html', {'seo': seo, 'catalog': data})


def exhibitions(request):
    # Skupiny s jedinou výstavou nedávají jako samostatná „cesta“ smysl —
    # zobrazí se pod hlavní timeline jako stručná zmínka. Jakmile by jich
    # v některé skupině přibylo, vrátí se do timeline automaticky.
    timelines, mentions = [], []
    queryset = list(Exhibition.objects.order_by('place', 'order'))
    for place, group in groupby(queryset, key=attrgetter('place')):
        items = list(group)
        (timelines if len(items) > 1 else mentions).append(
            {'place': place, 'items': items}
        )

    seo = PageMeta(
        title=fit_title(_('Výstavy'), SUFFIX, _(' | Kutná Hora, Praha, zahraničí')),
        description=_(
            'Výstavy malíře Oldřicha Lajska od roku 1956: Kutná Hora, Praha, Pražské '
            'salony v Jízdárně Pražského hradu i zahraničí – Lodž, Katovice a Paříž.'
        ),
        breadcrumbs=[(_('Výstavy'), reverse('core:exhibitions'))],
        schema=[schema.exhibition_event(item) for item in queryset],
    )
    context = {'seo': seo, 'timelines': timelines, 'mentions': mentions}
    return render(request, 'core/exhibitions.html', context)


def press(request):
    quotes = PressMention.objects.filter(kind='quote')
    publications = PressMention.objects.filter(kind='publication')
    seo = PageMeta(
        title=fit_title(_('Napsali o něm'), SUFFIX, _(' | citáty a bibliografie')),
        description=_(
            'Co o malíři Oldřichu Lajskovi napsali teoretici umění a kritici – citáty '
            'o jeho krajinomalbě, tvorbě a osobnosti a bibliografie publikací o jeho díle.'
        ),
        breadcrumbs=[(_('Napsali o něm'), reverse('core:press'))],
        # Citáty se nepřekládají strojově; EN verze má smysl, až budou přeložené.
        translated=not PressMention.objects.filter(text_en='').exists(),
    )
    context = {'seo': seo, 'quotes': quotes, 'publications': publications}
    return render(request, 'core/press.html', context)


def links(request):
    seo = PageMeta(
        title=fit_title(_('Odkazy'), SUFFIX, _(' v galeriích a databázích')),
        description=_(
            'Dílo Oldřicha Lajska v galeriích a databázích: Východočeská galerie '
            'v Pardubicích, Galerie výtvarného umění v Ostravě, knihovna UPM a Wikipedie.'
        ),
        breadcrumbs=[(_('Odkazy'), reverse('core:links'))],
    )
    return render(request, 'core/links.html', {'seo': seo, 'links': ExternalLink.objects.all()})


def contact(request):
    initial = {}
    painting_code = request.GET.get('obraz')
    if painting_code:
        initial['message'] = _(
            'Dobrý den,\nmám zájem o obraz s kódem „%(code)s“. '
            'Prosím o zaslání bližších informací.'
        ) % {'code': painting_code}

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Děkujeme za zprávu, ozveme se vám co nejdříve.'))
            return redirect(reverse('core:contact'))
    else:
        form = ContactForm(initial=initial)

    seo = PageMeta(
        title=fit_title(_('Kontakt'), _(' – poptávka obrazů Oldřicha Lajska')),
        description=_(
            'Máte zájem o obraz Oldřicha Lajska z pozůstalosti? Napište nám přes formulář '
            'a uveďte kód díla (např. K1). Odpovídá syn malíře JUDr. Jan Lajsek.'
        ),
        breadcrumbs=[(_('Kontakt'), reverse('core:contact'))],
        translated=content.has_translation('kontakt'),
    )
    context = {
        'seo': seo,
        'form': form,
        'paragraphs': content.paragraphs('kontakt'),
        'untranslated': content.is_untranslated('kontakt'),
    }
    return render(request, 'core/contact.html', context)
