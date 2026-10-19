"""Úvodní texty kategorií (CS/EN).

Vychází výhradně z textů původního webu (Dílo, Život, Napsali o něm).
Doplní se jen do prázdných polí — text upravený v adminu se nepřepíše.
"""

from django.db import migrations

OFFER_CS = (
    'Každý obraz v nabídce má svůj kód, podle kterého ho můžete nezávazně poptat; '
    'u části obrazů jsou uvedené i rozměry ověřené podle souhrnného katalogu.'
)
OFFER_EN = (
    'Every painting on offer has its own code, which you can use to send a no-obligation '
    'enquiry; for some paintings the dimensions verified against the catalogue are also given.'
)

INTROS = {
    'krajinomalba': (
        [
            'Krajinomalba je oblastí, v níž se Oldřich Lajsek (1925–2001) proslavil bezesporu '
            'nejvíce – patřil v ní mezi nejvýznamnější tvůrce své doby. Teoretik Vlastimil Vinter '
            'jej řadil mezi přední představitele soudobé české krajinomalby.',

            'Inspiraci čerpal hlavně ve Středočeském kraji, zejména ve svém rodném kutnohorském '
            'regionu. Často maloval krajiny z okolí hory Říp, z Polabí a z Českého středohoří. '
            'Součástí jeho tvorby jsou také obrazy ze zahraničních cest, především z Řecka, kde mu '
            'učarovaly architektonické vykopávky v okolí Delf, a scenérie z četných výjezdů do '
            'Jugoslávie.',

            'Pro jeho rukopis je typická pevná výstavba kompozice a zároveň mírné abstrahování. '
            'Své dílo vystavoval mimo jiné na přehlídkách výtvarného umění v Jízdárně Pražského '
            'hradu.',

            'V této kategorii najdete originální krajiny z autorovy pozůstalosti – obrazy českého '
            'malíře 20. století, které se hodí do sbírky i do interiéru. ' + OFFER_CS,
        ],
        [
            'Landscape painting is the field in which Oldřich Lajsek (1925–2001) became best '
            'known – he was among the most important landscape painters of his time. The critic '
            'Vlastimil Vinter counted him among the leading representatives of contemporary Czech '
            'landscape painting.',

            'He drew his inspiration mainly from Central Bohemia, above all from his native '
            'Kutná Hora region. He often painted landscapes around Říp Mountain, the Elbe lowlands '
            'and the Bohemian Central Uplands. His work also includes paintings from journeys '
            'abroad, especially Greece, where he was captivated by the archaeological sites around '
            'Delphi, and scenes from his many trips to Yugoslavia.',

            'His style is marked by a firmly built composition combined with gentle abstraction. '
            'Among other venues, he exhibited at the art shows in the Riding School of Prague Castle.',

            "This category contains original landscapes from the artist's estate – works by a "
            'twentieth-century Czech painter suited to a collection or an interior. ' + OFFER_EN,
        ],
    ),
    'abstrakce': (
        [
            'Abstraktní malba má v díle Oldřicha Lajska (1925–2001) zvláštní místo. V době '
            'uvolnění za éry „zlatých šedesátých let“ patřil k průkopníkům abstraktní malby. Kvůli '
            'jejímu následnému zákazu však musel tuto tvorbu v dalších letech – podobně jako '
            'například ikonografii – značně omezit.',

            'Právě abstrakce je dnes mezi sběrateli jeho díla velice oblíbená. Ukázkou abstraktní '
            'tvorby je obraz Zrcadlo, který najdete na stránce o autorově díle. Vedle malby se '
            'věnoval také grafice, užité grafice (plakáty, poutače, katalogy) a designu.',

            'Pro celou jeho tvorbu je typický osobitý umělecký rukopis s pevnou výstavbou '
            'kompozice. Prof. Ilja Bojanovský, bývalý rektor AMU, o něm napsal: „Oldřich Lajsek je '
            'uměleckou osobností charakterizovanou vyzrálostí tvůrčího stylu a neobyčejnou '
            'zkušeností.“',

            'V této kategorii jsou originální abstraktní obrazy z autorovy pozůstalosti – díla '
            'české malby 20. století, která se hodí do sbírky i do moderního interiéru. ' + OFFER_CS,
        ],
        [
            'Abstract painting holds a special place in the work of Oldřich Lajsek (1925–2001). '
            'During the relaxation of the “golden sixties” he was among the pioneers of abstract '
            'painting. When it was subsequently banned, he had to restrict this work considerably '
            'in the following years – as he did, for example, with iconography.',

            'Today it is precisely his abstraction that is especially popular with collectors. An '
            'example of his abstract work is the painting Mirror (Zrcadlo), shown on the page about '
            "the artist's work. Besides painting he also worked in printmaking, applied graphics "
            '(posters, catalogues) and design.',

            'His whole work is marked by a distinctive style with a firmly built composition. '
            'Prof. Ilja Bojanovský, former rector of the Academy of Performing Arts in Prague, '
            'described him as an artistic personality characterised by a mature creative style '
            'and exceptional experience.',

            "This category contains original abstract paintings from the artist's estate – "
            'twentieth-century Czech works suited to a collection or a modern interior. ' + OFFER_EN,
        ],
    ),
    'realismus': (
        [
            'Realistická díla tvoří rozsáhlou část tvorby Oldřicha Lajska (1925–2001). Jeho dílo '
            'velice poznamenala doba, ve které žil a tvořil – tehdejší totalitní ideologie nebyla '
            'zdaleka nakloněna všem žánrům. Stejně jako mnozí další byl proto nucen hledat '
            'ideologicky „nezávadné“ žánry jako jistou formu „úniku“; k nim patřily právě '
            'realistické obrazy a květinová zátiší.',

            'Četná jsou díla z pražského prostředí, kde rád zachycoval jedinečnost okamžiku '
            'v ulicích. Ukázkou realistické tvorby je obraz Ráno v Praze na stránce o autorově díle.',

            'Pro celou jeho tvorbu je typická pevná výstavba kompozice a mírné abstrahování. Mezi '
            'sběratele jeho tvorby patřil například herec Radovan Lukavský či spisovatel Karel '
            'Štorkán. Autorovo dílo je zastoupeno například v Galerii Mánes, ve Východočeské '
            'galerii v Pardubicích či v Galerii výtvarného umění v Ostravě.',

            'V této kategorii jsou originální realistické obrazy z autorovy pozůstalosti. ' + OFFER_CS,
        ],
        [
            'Realistic works form a large part of the output of Oldřich Lajsek (1925–2001). His '
            'work was strongly marked by the era in which he lived – the totalitarian ideology of '
            'the time was far from open to all genres. Like many others, he had to look for '
            'ideologically “harmless” genres as a form of “escape”; realistic paintings and floral '
            'still lifes were among them.',

            'Many works depict Prague, where he liked to capture the uniqueness of a moment in the '
            'streets. An example of his realistic work is the painting Morning in Prague, shown on '
            "the page about the artist's work.",

            'His whole work is marked by a firmly built composition and gentle abstraction. His '
            'collectors included the actor Radovan Lukavský and the writer Karel Štorkán. His '
            'work is held, for example, by the Mánes Gallery, the East Bohemian Gallery in '
            'Pardubice and the Gallery of Fine Arts in Ostrava.',

            "This category contains original realistic paintings from the artist's estate. " + OFFER_EN,
        ],
    ),
    'kvetinova-zatisi': (
        [
            'Květinová zátiší patří k rozsáhlým oblastem tvorby Oldřicha Lajska (1925–2001). Spolu '
            's realistickými obrazy patřila k ideologicky „nezávadným“ žánrům, k nimž se autor – '
            'stejně jako mnoho dalších umělců – v době totalitních omezení uchyloval jako k jisté '
            'formě „úniku“. Abstraktní malbu, v níž v 60. letech patřil k průkopníkům, musel po '
            'jejím zákazu značně omezit.',

            'Pro jeho tvorbu je charakteristický osobitý umělecký rukopis: pevná výstavba kompozice '
            'spojená s mírným abstrahováním. Malíř, grafik, designér a pedagog Oldřich Lajsek '
            'vytvořil za svůj život zhruba 3000 malířských a grafických děl, z nichž více než 1800 '
            'skončilo v soukromých sbírkách. Jeho obrazy jsou zastoupeny také v zahraničních '
            'galeriích, zejména v Německu, Francii a Polsku.',

            'V této kategorii jsou originální květinová zátiší z autorovy pozůstalosti – obrazy '
            'českého malíře 20. století, které se hodí do sbírky, do interiéru i jako dárek. '
            + OFFER_CS,
        ],
        [
            'Floral still lifes are one of the large areas of the work of Oldřich Lajsek '
            '(1925–2001). Together with realistic paintings they belonged to the ideologically '
            '“harmless” genres to which the artist – like many others – turned as a form of '
            '“escape” under totalitarian restrictions. Abstract painting, in which he was a pioneer '
            'in the 1960s, he had to restrict considerably after it was banned.',

            'His work is marked by a distinctive style: a firmly built composition combined with '
            'gentle abstraction. The painter, graphic artist, designer and teacher created around '
            '3,000 paintings and prints during his life, more than 1,800 of which ended up in '
            'private collections. His paintings are also held by galleries abroad, especially in '
            'Germany, France and Poland.',

            "This category contains original floral still lifes from the artist's estate – works "
            'by a twentieth-century Czech painter suited to a collection, an interior or as a gift. '
            + OFFER_EN,
        ],
    ),
}


def fill(apps, schema_editor):
    Category = apps.get_model('gallery', 'Category')
    for slug, (cs, en) in INTROS.items():
        category = Category.objects.filter(slug=slug).first()
        if category is None:
            continue
        changed = []
        if not category.intro:
            category.intro = '\n\n'.join(cs)
            changed.append('intro')
        if not category.intro_en:
            category.intro_en = '\n\n'.join(en)
            changed.append('intro_en')
        if changed:
            category.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0004_category_intro'),
    ]

    operations = [
        migrations.RunPython(fill, migrations.RunPython.noop),
    ]
