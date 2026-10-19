from itertools import groupby
from operator import attrgetter

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from gallery.models import Category

from . import articles, content, schema
from .forms import ContactForm
from .images import image_size
from .models import Exhibition, ExternalLink, PressMention
from .seo import PageMeta, absolute, fit_title
from .seo import default_image as seo_default_image

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
    # Z kapitol životopisu vedou odkazy na související články a obrazy.
    section_links = {
        'detstvi-a-kutna-hora': [(_('Oldřich Lajsek a Kutná Hora'), reverse('core:article-kutna-hora'))],
        'odboj': [(_('Odboj – organizace Pěst'), reverse('core:article-odboj-pest'))],
        'pedagog-a-sups': [(_('Skupina Směr'), reverse('core:article-skupina-smer'))],
        'skupina-smer': [
            (_('Skupina Směr'), reverse('core:article-skupina-smer')),
            (_('Abstrakce'), reverse('gallery:category_detail', args=['abstrakce'])),
        ],
        'pozdni-tvorba': [
            (_('Dílo'), reverse('core:work')),
            (_('Obrazy z pozůstalosti'), reverse('gallery:painting_list')),
        ],
    }
    sections = content.biography_sections()
    for section in sections:
        section['links'] = section_links.get(section['id'], [])
    context = {
        'seo': seo,
        'sections': sections,
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
        'categories': Category.objects.all(),
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
            # Samostatná adresa poděkování = měřitelná konverze v analytice.
            return redirect(reverse('core:contact_thanks'))
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


def contact_thanks(request):
    seo = PageMeta(
        title=fit_title(_('Děkujeme za zprávu'), SUFFIX),
        description=_(
            'Děkujeme za zprávu. Na poptávky obrazů Oldřicha Lajska odpovídá syn malíře '
            'JUDr. Jan Lajsek; mezitím si můžete prohlédnout další obrazy z pozůstalosti.'
        ),
        breadcrumbs=[(_('Kontakt'), reverse('core:contact')),
                     (_('Děkujeme'), reverse('core:contact_thanks'))],
    )
    return render(request, 'core/contact_thanks.html', {'seo': seo})


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /i18n/',
        '',
        f'Sitemap: {settings.SITE_URL.rstrip("/")}/sitemap.xml',
        '',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


def article(request, slug):
    """Obsahová stránka z core/articles.py (Jak koupit, Pravost, Kutná Hora…)."""
    meta, text = articles.localized(slug)
    url = reverse(f'core:article-{slug}')
    # Neověřené odstavce (TODO) vidí jen přihlášený správce — jako výzvu k doplnění.
    show_todo = request.user.is_staff

    sections = []
    for section in text['sections']:
        paragraphs = [
            {'text': paragraph, 'todo': articles.is_todo(paragraph)}
            for paragraph in section['paragraphs']
            if show_todo or not articles.is_todo(paragraph)
        ]
        if not paragraphs:
            continue
        sections.append({
            'id': section['id'],
            'heading': section['heading'],
            'paragraphs': paragraphs,
            'links': [(label, reverse(name, args=args))
                      for label, name, args in section.get('links', [])],
        })

    faq = [
        {'question': question, 'answer': answer, 'todo': articles.is_todo(answer)}
        for question, answer in text.get('faq', [])
        if show_todo or not articles.is_todo(answer)
    ]
    public_faq = [(item['question'], item['answer']) for item in faq if not item['todo']]

    crumbs = []
    if meta['parent'] == 'biography':
        crumbs.append((_('O autorovi'), reverse('core:biography')))
    crumbs.append((text['title'], url))

    image = None
    figure = meta.get('image')
    if figure:
        size = image_size(figure['path'])
        image = {
            'url': absolute(settings.MEDIA_URL + figure['path']),
            'width': size[0] if size else None,
            'height': size[1] if size else None,
            'alt': figure['caption'],
        }

    seo_schema = []
    if meta['schema'] == 'faq' and public_faq:
        seo_schema.append(schema.faq_page(public_faq))
    else:
        seo_schema.append(schema.article(
            text['title'], text['description'], url,
            image['url'] if image else seo_default_image()['url'],
        ))

    seo = PageMeta(
        title=text['meta_title'],
        description=text['description'],
        image=image,
        breadcrumbs=crumbs,
        schema=seo_schema,
        og_type='article',
    )
    context = {
        'seo': seo,
        'article': text,
        'sections': sections,
        'faq': faq,
        'figure': figure,
        'show_signature': meta.get('show_signature', False),
    }
    return render(request, 'core/article.html', context)
