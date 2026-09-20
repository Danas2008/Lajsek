from .models import Category


def nav_categories(request):
    """Kategorie obrazů pro rozbalovací menu v hlavičce."""
    return {'nav_categories': Category.objects.all()}
