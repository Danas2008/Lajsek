from django.db import migrations, models


def mark_wikipedia(apps, schema_editor):
    """Wikipedie je jediný odkaz, který je s jistotou celý o autorovi."""
    ExternalLink = apps.get_model('core', 'ExternalLink')
    ExternalLink.objects.filter(url__contains='wikipedia.org').update(is_profile=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_externallink_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='externallink',
            name='is_profile',
            field=models.BooleanField(
                default=False, verbose_name='profil autora',
                help_text='Zaškrtněte u stránek, které jsou celé o Oldřichu Lajskovi '
                          '(např. Wikipedie). Vyhledávače je propojí s autorem; '
                          'katalogy knihoven a galerií nezaškrtávejte.'),
        ),
        migrations.RunPython(mark_wikipedia, migrations.RunPython.noop),
    ]
