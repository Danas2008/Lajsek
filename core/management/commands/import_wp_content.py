"""Naplní databázi obsahem staženým z původního webu lajsek.cz.

Obrázky se očekávají už stažené v MEDIA_ROOT (media/paintings/<slug>/...,
media/pages/...). Příkaz je idempotentní — lze jej spustit opakovaně.
"""

import json

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Exhibition, ExternalLink, PressMention
from gallery.models import Category, Painting

DATA_FILE = settings.BASE_DIR / 'data' / 'wp_content.json'


class Command(BaseCommand):
    help = 'Importuje obsah z data/wp_content.json (staženo z lajsek.cz).'

    def handle(self, *args, **options):
        with open(DATA_FILE, encoding='utf-8') as fh:
            data = json.load(fh)

        cat_count = painting_count = 0
        for cat_order, cat in enumerate(data['categories']):
            category, _ = Category.objects.update_or_create(
                slug=cat['slug'],
                defaults={'name': cat['name'], 'order': cat_order},
            )
            cat_count += 1
            for order, item in enumerate(cat['paintings']):
                Painting.objects.update_or_create(
                    title=item['title'],
                    category=category,
                    defaults={
                        'image': item['image'],
                        'image_alt': f"Oldřich Lajsek — {cat['name'].lower()}, obraz {item['title']}",
                        'availability': 'available',
                        'order': order,
                    },
                )
                painting_count += 1

        for order, ex in enumerate(data['exhibitions']):
            Exhibition.objects.update_or_create(
                title=ex['title'],
                year=ex['year'],
                place=ex['place'],
                defaults={'order': order},
            )

        for order, pm in enumerate(data['press']):
            PressMention.objects.update_or_create(
                source=pm['source'],
                text=pm['text'],
                defaults={'kind': pm['kind'], 'order': order},
            )

        for order, link in enumerate(data['links']):
            ExternalLink.objects.update_or_create(
                url=link['url'],
                defaults={'title': link['title'], 'order': order},
            )

        self.stdout.write(self.style.SUCCESS(
            f'Kategorie: {cat_count} | Obrazy: {painting_count} | '
            f'Výstavy: {Exhibition.objects.count()} | '
            f'Napsali o něm: {PressMention.objects.count()} | '
            f'Odkazy: {ExternalLink.objects.count()}'
        ))
