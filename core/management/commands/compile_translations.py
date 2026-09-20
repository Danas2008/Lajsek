"""Zkompiluje .po na .mo bez nutnosti mít nainstalovaný GNU gettext.

Na Windows bývá `compilemessages` nepoužitelný, protože chybí msgfmt.
Použití: python manage.py compile_translations
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Zkompiluje prekladove katalogy (.po na .mo) pomoci polib.'

    def handle(self, *args, **options):
        try:
            import polib
        except ImportError as exc:
            raise CommandError('Chybí knihovna polib — nainstaluj: pip install polib') from exc

        compiled = 0
        for locale_dir in settings.LOCALE_PATHS:
            for po_path in sorted(locale_dir.glob('*/LC_MESSAGES/*.po')):
                po = polib.pofile(str(po_path))
                mo_path = po_path.with_suffix('.mo')
                po.save_as_mofile(str(mo_path))
                compiled += 1
                self.stdout.write(
                    f'{po_path.parent.parent.name}: {len(po)} retezcu -> {mo_path.name}'
                )

        if not compiled:
            self.stdout.write(self.style.WARNING('Nenalezeny žádné .po soubory.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Zkompilováno katalogů: {compiled}'))
