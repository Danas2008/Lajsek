"""Obsahové stránky (Jak koupit, Pravost, Kutná Hora, Skupina Směr, Odboj).

Fakta pocházejí výhradně z životopisu a textů původního webu
(data/wp_content.json) a z údajů o katalogu. Co ověřit nejde, je označeno
„TODO(rodina):“ — takový odstavec (nebo otázku FAQ) web veřejnosti
nezobrazí, uvidí ho jen přihlášený správce jako výzvu k doplnění.
Po doplnění stačí prefix smazat.

Odkazy v sekcích: (popisek, url name, argumenty).
"""

from django.utils.translation import get_language

TODO = 'TODO(rodina):'

ARTICLES = {
    # ------------------------------------------------------------------
    'jak-koupit': {
        'path': 'jak-koupit/',
        'parent': None,
        'schema': 'faq',
        'cs': {
            'title': 'Jak koupit obraz Oldřicha Lajska',
            'meta_title': 'Jak koupit obraz – Oldřich Lajsek | originály z pozůstalosti',
            'description': (
                'Jak koupit originální obraz Oldřicha Lajska z pozůstalosti: vyberte dílo, '
                'pošlete poptávku s kódem (např. K1) a domluvte se přímo s rodinou autora.'
            ),
            'lead': (
                'Všechny obrazy v nabídce pocházejí z pozůstalosti malíře Oldřicha Lajska '
                '(1925–2001). Koupě probíhá přímo s rodinou autora.'
            ),
            'sections': [
                {'id': 'vyber', 'heading': '1. Vyberte obraz', 'paragraphs': [
                    'Obrazy jsou rozdělené do čtyř kategorií: krajinomalba, abstrakce, realismus '
                    'a květinová zátiší. Každý obraz má vlastní kód (např. K1), který je uvedený '
                    'u obrazu i pod jeho náhledem v galerii. Podle tohoto kódu obraz poptáte.',
                ], 'links': [
                    ('Krajinomalba', 'gallery:category_detail', ['krajinomalba']),
                    ('Abstrakce', 'gallery:category_detail', ['abstrakce']),
                    ('Realismus', 'gallery:category_detail', ['realismus']),
                    ('Květinová zátiší', 'gallery:category_detail', ['kvetinova-zatisi']),
                ]},
                {'id': 'poptavka', 'heading': '2. Pošlete poptávku', 'paragraphs': [
                    'Na stránce obrazu klikněte na tlačítko „Mám zájem o tento obraz“. Otevře se '
                    'kontaktní formulář s předvyplněným kódem díla – stačí doplnit jméno a e-mail. '
                    'Na poptávky odpovídá syn malíře JUDr. Jan Lajsek.',
                    'Cena obrazů není na webu uvedena. Zeptejte se na ni přímo v poptávce.',
                ], 'links': [('Kontaktní formulář', 'core:contact', [])]},
                {'id': 'prohlidka', 'heading': '3. Prohlídka obrazu', 'paragraphs': [
                    TODO + ' Je možné si obraz před koupí prohlédnout osobně v Praze? Kde a jak se '
                    'prohlídka domlouvá?',
                ]},
                {'id': 'predani', 'heading': '4. Předání, platba a doprava', 'paragraphs': [
                    TODO + ' Jak probíhá předání (osobně / zaslání), platba a balení? Zasíláte '
                    'obrazy i do zahraničí?',
                ]},
                {'id': 'doklad', 'heading': '5. Doklad o původu', 'paragraphs': [
                    TODO + ' Vystavujete ke koupenému obrazu doklad o původu z pozůstalosti? '
                    'Co obsahuje (kód díla, rozměr, podpis)?',
                ], 'links': [('Pravost a provenience', 'core:article-pravost-a-provenience', [])]},
            ],
            'faq': [
                ('Jak poptat obraz Oldřicha Lajska?',
                 'Na stránce obrazu klikněte na „Mám zájem o tento obraz“, nebo napište přes '
                 'kontaktní formulář a uveďte kód díla (např. K1).'),
                ('Kde najdu kód díla?',
                 'Kód je uvedený u každého obrazu na webu – na stránce obrazu i pod jeho '
                 'náhledem v galerii.'),
                ('Odkud obrazy pocházejí?',
                 'Všechny nabízené obrazy pocházejí z pozůstalosti malíře Oldřicha Lajska '
                 '(1925–2001).'),
                ('Je na webu celé autorovo dílo?',
                 'Ne. Na webu je výběr obrazů z pozůstalosti. Souhrnný katalog eviduje 1053 děl '
                 's rozměry; za svůj život vytvořil Oldřich Lajsek zhruba 3000 malířských '
                 'a grafických děl.'),
                ('Kolik obraz stojí?',
                 'Ceny nejsou na webu zveřejněné. Na cenu konkrétního obrazu se zeptejte v poptávce.'),
                ('Lze obraz zaslat poštou nebo do zahraničí?', TODO + ' doplnit.'),
            ],
        },
        'en': {
            'title': 'How to buy a painting by Oldřich Lajsek',
            'meta_title': 'How to buy a painting – Oldřich Lajsek | from the estate',
            'description': (
                "How to buy a painting by Oldřich Lajsek from the artist's estate: choose a "
                'work, send an enquiry with its code (e.g. K1) and deal directly with his family.'
            ),
            'lead': (
                'All paintings on offer come from the estate of the painter Oldřich Lajsek '
                "(1925–2001). You buy directly from the artist's family."
            ),
            'sections': [
                {'id': 'vyber', 'heading': '1. Choose a painting', 'paragraphs': [
                    'The paintings are divided into four categories: landscapes, abstraction, '
                    'realism and floral still lifes. Every painting has its own code (e.g. K1), '
                    'shown on the painting page and under its thumbnail in the gallery. Use this '
                    'code in your enquiry.',
                ], 'links': [
                    ('Landscape painting', 'gallery:category_detail', ['krajinomalba']),
                    ('Abstraction', 'gallery:category_detail', ['abstrakce']),
                    ('Realism', 'gallery:category_detail', ['realismus']),
                    ('Floral still lifes', 'gallery:category_detail', ['kvetinova-zatisi']),
                ]},
                {'id': 'poptavka', 'heading': '2. Send an enquiry', 'paragraphs': [
                    'On the painting page, click “I am interested in this painting”. The contact '
                    'form opens with the code already filled in – just add your name and e-mail. '
                    "Enquiries are answered by the painter's son, JUDr. Jan Lajsek.",
                    'Prices are not listed on the website. Please ask about the price in your enquiry.',
                ], 'links': [('Contact form', 'core:contact', [])]},
                {'id': 'prohlidka', 'heading': '3. Viewing the painting', 'paragraphs': [
                    TODO + ' viewing in Prague – where and how to arrange it.',
                ]},
                {'id': 'predani', 'heading': '4. Handover, payment and shipping', 'paragraphs': [
                    TODO + ' handover, payment, packing, shipping abroad.',
                ]},
                {'id': 'doklad', 'heading': '5. Proof of provenance', 'paragraphs': [
                    TODO + ' proof of origin from the estate – what it contains.',
                ], 'links': [('Authenticity and provenance', 'core:article-pravost-a-provenience', [])]},
            ],
            'faq': [
                ('How do I enquire about a painting by Oldřich Lajsek?',
                 'On the painting page, click “I am interested in this painting”, or write via '
                 'the contact form and give the code of the work (e.g. K1).'),
                ('Where do I find the code of a work?',
                 'The code is shown for every painting on the website – on the painting page '
                 'and under its thumbnail in the gallery.'),
                ('Where do the paintings come from?',
                 'All paintings on offer come from the estate of the painter Oldřich Lajsek '
                 '(1925–2001).'),
                ("Is the artist's entire work on the website?",
                 'No. The website shows a selection of paintings from the estate. The '
                 'catalogue lists 1,053 works with dimensions; during his life Oldřich Lajsek '
                 'created around 3,000 paintings and prints.'),
                ('How much does a painting cost?',
                 'Prices are not published on the website. Please ask about the price of a '
                 'specific painting in your enquiry.'),
                ('Can a painting be shipped, including abroad?', TODO + ' to be completed.'),
            ],
        },
    },

    # ------------------------------------------------------------------
    'pravost-a-provenience': {
        'path': 'pravost-a-provenience/',
        'parent': None,
        'schema': 'article',
        'show_signature': True,
        'cs': {
            'title': 'Pravost a provenience obrazů',
            'meta_title': 'Pravost a provenience – obrazy Oldřicha Lajska',
            'description': (
                'Obrazy Oldřicha Lajska na tomto webu pocházejí přímo z pozůstalosti autora. '
                'Signatura, souhrnný katalog 1053 děl a zastoupení ve sbírkách a galeriích.'
            ),
            'lead': (
                'Obrazy nabízené na tomto webu pocházejí přímo z pozůstalosti malíře Oldřicha '
                'Lajska (1925–2001).'
            ),
            'sections': [
                {'id': 'pozustalost', 'heading': 'Původ z pozůstalosti', 'paragraphs': [
                    'Díla zůstala po autorově smrti v roce 2001 v rodině. Poptávky vyřizuje syn '
                    'malíře JUDr. Jan Lajsek.',
                    TODO + ' kde byla díla uložena a jak je jejich původ doložen '
                    '(soupis pozůstalosti, fotografie, dokumenty).',
                ], 'links': [('Jak koupit obraz', 'core:article-jak-koupit', [])]},
                {'id': 'signatura', 'heading': 'Signatura autora', 'paragraphs': [
                    'Níže je podoba autorova podpisu „O. Lajsek“. Podpis Oldřicha Lajska eviduje '
                    'také databáze Signatury malířů.',
                    'U obrazů, u kterých byla signatura ověřena, je to uvedeno na stránce obrazu '
                    'včetně jejího umístění.',
                ], 'links': [('Odkazy na databáze a galerie', 'core:links', [])]},
                {'id': 'katalog', 'heading': 'Souhrnný katalog', 'paragraphs': [
                    'Souhrnný katalog eviduje 1053 děl na 26 dvoustranách, řazených po kategoriích '
                    'a s uvedeným rozměrem. Kódy v katalogu se od kódů na webu liší – například '
                    'obraz K1 z webu je v katalogu veden jako R233. U obrazů, u nichž bylo '
                    'spárování s katalogem ověřeno porovnáním reprodukcí, uvádíme katalogový kód '
                    'na stránce obrazu.',
                ], 'links': [('Katalog ke stažení', 'core:catalog', [])]},
                {'id': 'sbirky', 'heading': 'Dílo ve sbírkách a galeriích', 'paragraphs': [
                    'Za svůj život vytvořil Oldřich Lajsek zhruba 3000 malířských nebo grafických '
                    'děl, z nichž více než 1800 skončilo v soukromých sbírkách. Mezi sběratele jeho '
                    'tvorby patřil například herec Radovan Lukavský či spisovatel Karel Štorkán.',
                    'Jeho dílo je zastoupeno v zahraničních galeriích, zejména v Německu, Francii '
                    'a Polsku. Z českých síní lze zmínit Galerii Mánes, Východočeskou galerii '
                    'v Pardubicích či Galerii výtvarného umění v Ostravě.',
                    TODO + ' existují k dílům odborné posudky nebo vyjádření znalců?',
                ], 'links': [('Dílo', 'core:work', [])]},
            ],
        },
        'en': {
            'title': 'Authenticity and provenance',
            'meta_title': 'Authenticity and provenance – paintings by Oldřich Lajsek',
            'description': (
                "The paintings by Oldřich Lajsek offered here come directly from the artist's "
                'estate. Signature, the catalogue of 1,053 works and presence in collections.'
            ),
            'lead': (
                'The paintings offered on this website come directly from the estate of the '
                'painter Oldřich Lajsek (1925–2001).'
            ),
            'sections': [
                {'id': 'pozustalost', 'heading': 'From the estate', 'paragraphs': [
                    "After the artist's death in 2001 the works remained with his family. "
                    "Enquiries are handled by the painter's son, JUDr. Jan Lajsek.",
                    TODO + ' where the works were kept and how their origin is documented.',
                ], 'links': [('How to buy a painting', 'core:article-jak-koupit', [])]},
                {'id': 'signatura', 'heading': "The artist's signature", 'paragraphs': [
                    "Below is the artist's signature “O. Lajsek”. His signature is also recorded "
                    'in the Signatury malířů database (signatures of painters).',
                    'Where a signature has been verified on a painting, this is stated on the '
                    'painting page together with its position.',
                ], 'links': [('Links to databases and galleries', 'core:links', [])]},
                {'id': 'katalog', 'heading': 'The catalogue', 'paragraphs': [
                    'The catalogue lists 1,053 works on 26 double pages, ordered by category and '
                    'with dimensions. Catalogue codes differ from the codes on this website – for '
                    'example painting K1 on the website is R233 in the catalogue. Where the match '
                    'with the catalogue has been verified by comparing reproductions, the '
                    'catalogue code is shown on the painting page.',
                ], 'links': [('Download the catalogue', 'core:catalog', [])]},
                {'id': 'sbirky', 'heading': 'Collections and galleries', 'paragraphs': [
                    'During his life Oldřich Lajsek created around 3,000 paintings and prints, more '
                    'than 1,800 of which ended up in private collections. His collectors included '
                    'the actor Radovan Lukavský and the writer Karel Štorkán.',
                    'His work is held by galleries abroad, especially in Germany, France and '
                    'Poland. Czech institutions include the Mánes Gallery, the East Bohemian '
                    'Gallery in Pardubice and the Gallery of Fine Arts in Ostrava.',
                    TODO + ' expert opinions on the works?',
                ], 'links': [('Work', 'core:work', [])]},
            ],
        },
    },

    # ------------------------------------------------------------------
    'kutna-hora': {
        'path': 'o-autorovi/kutna-hora/',
        'parent': 'biography',
        'schema': 'article',
        'image': {'path': 'pages/Křesetice.jpg', 'caption': 'Křesetice'},
        'cs': {
            'title': 'Oldřich Lajsek a Kutná Hora',
            'meta_title': 'Oldřich Lajsek a Kutná Hora – malíř z Křesetic',
            'description': (
                'Malíř Oldřich Lajsek se narodil v Křeseticích u Kutné Hory, v Kutné Hoře '
                'studoval a odtud čerpal inspiraci. Výstavy v Kutné Hoře 1956, 1985 a 2016.'
            ),
            'lead': (
                'Kutnohorsko bylo pro Oldřicha Lajska rodným krajem i trvalým zdrojem inspirace.'
            ),
            'sections': [
                {'id': 'kresetice', 'heading': 'Rodné Křesetice', 'paragraphs': [
                    'Oldřich Lajsek se narodil 8. února 1925 v Křeseticích nedaleko Kutné Hory '
                    'v rodině obchodníka.',
                ]},
                {'id': 'skola', 'heading': 'Školní léta v Kutné Hoře', 'paragraphs': [
                    'V Kutné Hoře vychodil obecnou i měšťanskou školu a roku 1944 maturoval na '
                    'tamní Vyšší průmyslové škole strojnické. Technické vzdělání ze strojní '
                    'průmyslovky poprvé spojil se svým výtvarným talentem za války v odboji.',
                ], 'links': [('Odboj – organizace Pěst', 'core:article-odboj-pest', [])]},
                {'id': 'inspirace', 'heading': 'Kutnohorsko v obrazech', 'paragraphs': [
                    'Inspiraci čerpal hlavně ve Středočeském kraji, zejména ve svém rodném '
                    'kutnohorském regionu. Bezesporu nejvíce se proslavil právě krajinomalbou, '
                    'v níž patřil mezi nejvýznamnější tvůrce své doby.',
                    TODO + ' které obrazy v nabídce zobrazují Kutnohorsko? (Po doplnění pole '
                    '„zobrazené místo“ u obrazu je lze odsud odkázat.)',
                ], 'links': [('Krajinomalba', 'gallery:category_detail', ['krajinomalba'])]},
                {'id': 'vystavy', 'heading': 'Výstavy v Kutné Hoře', 'paragraphs': [
                    'V Kutné Hoře vystavoval v letech 1956 a 1985. V roce 2016 se jeho dílo '
                    'představilo v kutnohorském Sankturinovském domě.',
                ], 'links': [('Všechny výstavy', 'core:exhibitions', [])]},
            ],
        },
        'en': {
            'title': 'Oldřich Lajsek and Kutná Hora',
            'meta_title': 'Oldřich Lajsek and Kutná Hora – a painter from Křesetice',
            'description': (
                'The painter Oldřich Lajsek was born in Křesetice near Kutná Hora, went to school '
                'in Kutná Hora and drew on the region. Exhibitions there in 1956, 1985 and 2016.'
            ),
            'lead': (
                'The Kutná Hora region was the birthplace of Oldřich Lajsek and a lasting '
                'source of inspiration.'
            ),
            'sections': [
                {'id': 'kresetice', 'heading': 'Born in Křesetice', 'paragraphs': [
                    'Oldřich Lajsek was born on 8 February 1925 in Křesetice near Kutná Hora into '
                    "a merchant's family.",
                ]},
                {'id': 'skola', 'heading': 'School years in Kutná Hora', 'paragraphs': [
                    'He attended primary and lower secondary school in Kutná Hora and in 1944 '
                    'graduated from the local Higher Industrial School of Mechanical Engineering. '
                    'He first combined this technical training with his artistic talent in the '
                    'resistance during the war.',
                ], 'links': [('The resistance – the Pěst organisation', 'core:article-odboj-pest', [])]},
                {'id': 'inspirace', 'heading': 'The Kutná Hora region in his paintings', 'paragraphs': [
                    'He drew his inspiration mainly from Central Bohemia, above all from his native '
                    'Kutná Hora region. He became best known for his landscape painting, in which '
                    'he was among the most important artists of his time.',
                    TODO + ' paintings showing the Kutná Hora region.',
                ], 'links': [('Landscape painting', 'gallery:category_detail', ['krajinomalba'])]},
                {'id': 'vystavy', 'heading': 'Exhibitions in Kutná Hora', 'paragraphs': [
                    'He exhibited in Kutná Hora in 1956 and 1985. In 2016 his work was shown at '
                    'the Sankturinovský House in Kutná Hora.',
                ], 'links': [('All exhibitions', 'core:exhibitions', [])]},
            ],
        },
    },

    # ------------------------------------------------------------------
    'skupina-smer': {
        'path': 'o-autorovi/skupina-smer/',
        'parent': 'biography',
        'schema': 'article',
        'cs': {
            'title': 'Skupina Směr',
            'meta_title': 'Skupina Směr (Skupina osmi výtvarníků) – Oldřich Lajsek',
            'description': (
                'Skupina osmi výtvarníků, od roku 1962 Směr: výtvarné těleso, které v roce 1960 '
                'založil a vedl malíř Oldřich Lajsek. Výchovné akce na vesnicích a výstavy.'
            ),
            'lead': (
                'Oldřich Lajsek byl vůdčí osobností při založení výtvarného tělesa, které od '
                'začátku vedl.'
            ),
            'sections': [
                {'id': 'zalozeni', 'heading': 'Založení skupiny', 'paragraphs': [
                    'V roce 1960 byl Oldřich Lajsek vůdčí osobností při založení výtvarného tělesa '
                    'nazvaného Skupina osmi výtvarníků, od roku 1962 přejmenovaného na Směr. '
                    'Ve skupině od začátku působil jako vedoucí.',
                ]},
                {'id': 'cile', 'heading': 'Cíle skupiny', 'paragraphs': [
                    'Cílem skupiny bylo zejména pořádání výtvarně výchovných akcí mimo zavedená '
                    'kulturní střediska, hlavně na vesnicích a v menších městech, a zároveň '
                    'hledání nových možností pro pořádání výstav. Díky skupině dodal své činnosti '
                    'i jistý sociální rozměr.',
                ]},
                {'id': 'souvislosti', 'heading': 'Souvislosti', 'paragraphs': [
                    'Skupina vznikla v době, kdy Lajsek už pět let působil jako profesor na '
                    'Střední uměleckoprůmyslové škole v Praze (od roku 1955) a byl členem Svazu '
                    'československých výtvarných umělců (od roku 1954). Výtvarná výchova ho '
                    'provázela od studií na Pedagogické fakultě Univerzity Karlovy.',
                    'Šedesátá léta byla dobou uvolnění, kdy Lajsek patřil k průkopníkům abstraktní '
                    'malby.',
                ], 'links': [
                    ('Život Oldřicha Lajska', 'core:life', []),
                    ('Abstrakce', 'gallery:category_detail', ['abstrakce']),
                ]},
                {'id': 'clenove', 'heading': 'Členové a výstavy skupiny', 'paragraphs': [
                    TODO + ' kdo byli členové skupiny, kde a kdy pořádala akce a výstavy?',
                ]},
            ],
        },
        'en': {
            'title': 'The Směr group',
            'meta_title': 'The Směr group (Group of Eight Artists) – Oldřich Lajsek',
            'description': (
                'The Group of Eight Artists, renamed Směr in 1962: an art group founded and led '
                'by the painter Oldřich Lajsek in 1960. Art education events and exhibitions.'
            ),
            'lead': (
                'Oldřich Lajsek was the leading figure in founding this art group, which he led '
                'from the start.'
            ),
            'sections': [
                {'id': 'zalozeni', 'heading': 'Founding the group', 'paragraphs': [
                    'In 1960 Oldřich Lajsek was the leading figure in founding an art group called '
                    'the Group of Eight Artists, renamed Směr (Direction) in 1962. He led the '
                    'group from the very beginning.',
                ]},
                {'id': 'cile', 'heading': "The group's aims", 'paragraphs': [
                    'The group mainly organised art education events outside the established '
                    'cultural centres, above all in villages and small towns, and looked for new '
                    'ways to stage exhibitions. Through the group his work also gained a social '
                    'dimension.',
                ]},
                {'id': 'souvislosti', 'heading': 'Context', 'paragraphs': [
                    'The group was founded when Lajsek had already been teaching for five years '
                    'at the Secondary School of Applied Arts in Prague (from 1955) and was a '
                    'member of the Union of Czechoslovak Artists (from 1954). Art education had '
                    'accompanied him since his studies at the Faculty of Education of Charles '
                    'University.',
                    'The 1960s were a time of relaxation in which Lajsek was among the pioneers '
                    'of abstract painting.',
                ], 'links': [
                    ('Life of Oldřich Lajsek', 'core:life', []),
                    ('Abstraction', 'gallery:category_detail', ['abstrakce']),
                ]},
                {'id': 'clenove', 'heading': 'Members and exhibitions', 'paragraphs': [
                    TODO + ' members, events and exhibitions of the group.',
                ]},
            ],
        },
    },

    # ------------------------------------------------------------------
    'odboj-pest': {
        'path': 'o-autorovi/odboj-pest/',
        'parent': 'biography',
        'schema': 'article',
        'cs': {
            'title': 'Odboj – organizace Pěst',
            'meta_title': 'Odboj – organizace Pěst | Oldřich Lajsek za války',
            'description': (
                'Za 2. světové války se Oldřich Lajsek zapojil do odboje v organizaci Pěst: tajně '
                'kopíroval výkresy zbraní pro partyzány. Po odhalení unikl popravě.'
            ),
            'lead': (
                'Během 2. světové války se Oldřich Lajsek aktivně účastnil odboje proti '
                'nacistické okupaci v organizaci Pěst.'
            ),
            'sections': [
                {'id': 'cinnost', 'heading': 'Kopie výkresů pro partyzány', 'paragraphs': [
                    'V odbojové činnosti mohl poprvé využít svého výtvarného talentu '
                    'a středoškolského technického vzdělání – roku 1944 maturoval na Vyšší '
                    'průmyslové škole strojnické v Kutné Hoře. V konstrukční kanceláři vždy tajně '
                    'vyhotovoval kopie výkresové dokumentace k vojenským zbraním, na jejichž '
                    'základě posléze dopomáhal k vyzbrojování partyzánů.',
                ], 'links': [('Oldřich Lajsek a Kutná Hora', 'core:article-kutna-hora', [])]},
                {'id': 'odhaleni', 'heading': 'Odhalení', 'paragraphs': [
                    'Později byl odhalen; popravě se vyhnul jen díky blížícímu se konci války.',
                ]},
                {'id': 'csbs', 'heading': 'Český svaz bojovníků za svobodu', 'paragraphs': [
                    'Za svoji odbojovou činnost se posléze stal členem Českého svazu bojovníků '
                    'za svobodu.',
                    TODO + ' kde sídlila konstrukční kancelář, existují dokumenty nebo svědectví '
                    'o jeho odbojové činnosti?',
                ], 'links': [('Život Oldřicha Lajska', 'core:life', [])]},
            ],
        },
        'en': {
            'title': 'The resistance – the Pěst organisation',
            'meta_title': 'The resistance – Pěst | Oldřich Lajsek in the war',
            'description': (
                'In the Second World War Oldřich Lajsek joined the resistance group Pěst, secretly '
                'copying weapon drawings for partisans. Discovered, he escaped execution.'
            ),
            'lead': (
                'During the Second World War Oldřich Lajsek took an active part in the resistance '
                'against the Nazi occupation in the organisation Pěst (Fist).'
            ),
            'sections': [
                {'id': 'cinnost', 'heading': 'Copying drawings for the partisans', 'paragraphs': [
                    'In the resistance he could use his artistic talent and technical education '
                    'for the first time – in 1944 he had graduated from the Higher Industrial '
                    'School of Mechanical Engineering in Kutná Hora. In a design office he '
                    'secretly made copies of technical drawings of military weapons, which then '
                    'helped to arm the partisans.',
                ], 'links': [('Oldřich Lajsek and Kutná Hora', 'core:article-kutna-hora', [])]},
                {'id': 'odhaleni', 'heading': 'Discovered', 'paragraphs': [
                    'He was later discovered; he escaped execution only because the war was '
                    'coming to an end.',
                ]},
                {'id': 'csbs', 'heading': 'Czech Union of Freedom Fighters', 'paragraphs': [
                    'For his resistance activities he later became a member of the Czech Union of '
                    'Freedom Fighters.',
                    TODO + ' location of the design office, documents or testimonies.',
                ], 'links': [('Life of Oldřich Lajsek', 'core:life', [])]},
            ],
        },
    },
}


def is_todo(text):
    return text.startswith(TODO)


def localized(slug):
    """Obsah článku v aktuálním jazyce (EN je u všech článků k dispozici)."""
    article = ARTICLES[slug]
    lang = 'en' if get_language() == 'en' else 'cs'
    return article, article[lang]
