"""Rozšířené údaje o obraze (rok jako číslo, technika z nabídky, motiv,
signatura, kód v katalogu, alt texty CS/EN).

Převod existujících dat je opatrný — na produkci mohl správce staré
textové hodnoty už vyplnit:
- rok: vezme se první čtyřmístné číslo, „cca“/„kol.“/rozpětí = přibližný,
- technika: známé názvy se převedou na volbu, ostatní zůstanou doslova
  v „upřesnění techniky“ s volbou „jiná“,
- alt text: automaticky vytvořené texty z importu („Oldřich Lajsek —
  krajinomalba, obraz K1“) se smažou, aby je nahradil generátor.
  Ručně psané texty zůstávají.
"""

import re

from django.db import migrations, models

TECHNIQUE_ALIASES = {
    'olej na plátně': 'oil_canvas',
    'olej na platne': 'oil_canvas',
    'olej na sololitu': 'oil_hardboard',
    'akvarel': 'watercolour',
    'tempera': 'tempera',
    'kvaš': 'gouache',
    'kvas': 'gouache',
    'grafika': 'print',
    'kombinovaná technika': 'mixed',
}
AUTO_ALT = re.compile(r'^Oldřich Lajsek — .+, obraz \S+$')


def forwards(apps, schema_editor):
    Painting = apps.get_model('gallery', 'Painting')
    for painting in Painting.objects.all():
        changed = []

        old_year = (painting.year_text or '').strip()
        match = re.search(r'\d{4}', old_year)
        if match:
            painting.year = int(match.group())
            painting.year_approx = bool(
                re.search(r'cca|kol|asi|~|\?|[-–]', old_year, re.IGNORECASE)
            )
            changed += ['year', 'year_approx']

        old_technique = (painting.technique or '').strip()
        if old_technique:
            key = TECHNIQUE_ALIASES.get(old_technique.lower())
            if key is None:
                painting.technique_detail = old_technique
                key = 'other'
                changed.append('technique_detail')
            painting.technique = key
            changed.append('technique')

        if AUTO_ALT.match(painting.alt_text_cs or ''):
            painting.alt_text_cs = ''
            changed.append('alt_text_cs')

        if changed:
            painting.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0002_category_name_en_painting_description_en_and_more'),
    ]

    operations = [
        # --- pole, která se převádějí z dat ---------------------------------
        migrations.RenameField('painting', 'year', 'year_text'),
        migrations.AddField(
            model_name='painting',
            name='year',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name='rok vzniku',
                help_text='Jen čtyřmístný rok, např. 1965. Neznámý rok nechte prázdný.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='year_approx',
            field=models.BooleanField(
                default=False, verbose_name='rok je přibližný',
                help_text='Zaškrtněte, pokud rok není jistý — web zobrazí „cca 1965“.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='technique_detail',
            field=models.CharField(
                blank=True, max_length=150, verbose_name='upřesnění techniky',
                help_text='Nepovinné, např. „olej a pastel na kartonu“. '
                          'V české verzi se zobrazí místo vybrané techniky.'),
        ),
        migrations.RenameField('painting', 'image_alt', 'alt_text_cs'),
        migrations.AlterField(
            model_name='painting',
            name='alt_text_cs',
            field=models.CharField(
                blank=True, max_length=250, verbose_name='alt text',
                help_text='Popis obrázku pro nevidomé a vyhledávače. Prázdné = vytvoří se '
                          'automaticky z vyplněných údajů (viz „Automatický alt text“).'),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.RemoveField('painting', 'year_text'),
        migrations.AlterField(
            model_name='painting',
            name='technique',
            field=models.CharField(
                blank=True, max_length=30, verbose_name='technika',
                choices=[
                    ('oil_canvas', 'olej na plátně'),
                    ('oil_hardboard', 'olej na sololitu'),
                    ('watercolour', 'akvarel'),
                    ('tempera', 'tempera'),
                    ('gouache', 'kvaš'),
                    ('print', 'grafika'),
                    ('mixed', 'kombinovaná technika'),
                    ('other', 'jiná'),
                ],
                help_text='Vyberte, jen pokud je technika jistá.'),
        ),

        # --- jen nápověda v adminu ---------------------------------------
        migrations.AlterField(
            model_name='painting',
            name='description',
            field=models.TextField(
                blank=True, verbose_name='popis',
                help_text='Volný text o obraze. Začátek textu se použije i jako popis pro vyhledávače.'),
        ),
        migrations.AlterField(
            model_name='painting',
            name='dimensions',
            field=models.CharField(
                blank=True, max_length=100, verbose_name='rozměry',
                help_text='Šířka × výška v centimetrech, např. „76×63 cm“.'),
        ),
        migrations.AlterField(
            model_name='painting',
            name='display_title',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='název obrazu',
                help_text='Skutečný název díla, je-li znám, např. „Ráno v Praze“. '
                          'Prázdné = použije se „kategorie + kód“ (Krajinomalba K1). '
                          'Po vyplnění se změní adresa stránky; stará adresa dál funguje.'),
        ),

        # --- nová pole -----------------------------------------------------
        migrations.AddField(
            model_name='painting',
            name='alt_text_en',
            field=models.CharField(
                blank=True, max_length=250, verbose_name='alt text (EN)',
                help_text='Nepovinné. Prázdné = vytvoří se automaticky v angličtině.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='catalog_code',
            field=models.CharField(
                blank=True, max_length=20, verbose_name='kód v souhrnném katalogu',
                help_text='Označení v Katalog.pdf (např. R233) — liší se od kódu na webu. '
                          'Doplňuje ho příkaz apply_catalog_dimensions z ověřených párů.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='display_title_en',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='název obrazu (EN)',
                help_text='Nepovinné, např. „Morning in Prague“. Prázdné = použije se český název.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='motif',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='motiv',
                help_text='Co obraz zobrazuje, např. „horská krajina v zimě“, „kytice slunečnic“.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='motif_en',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='motiv (EN)',
                help_text='Nepovinné, např. „mountain landscape in winter“.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='location_depicted',
            field=models.CharField(
                blank=True, max_length=200, verbose_name='zobrazené místo',
                help_text='Konkrétní místo na obraze, je-li jisté, např. „Krkonoše“, „Ještěd“, '
                          '„Kutná Hora“. Píše se česky, použije se v obou jazycích.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='is_signed',
            field=models.BooleanField(
                blank=True, null=True, verbose_name='signováno',
                help_text='„Neznámo“ nechte, dokud signaturu na obraze nikdo neověřil.'),
        ),
        migrations.AddField(
            model_name='painting',
            name='signature_position',
            field=models.CharField(
                blank=True, max_length=100, verbose_name='umístění signatury',
                help_text='Např. „vpravo dole“, „na rubu“.'),
        ),
    ]
