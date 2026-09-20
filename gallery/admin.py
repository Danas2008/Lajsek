from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Painting


class HasRealTitleFilter(admin.SimpleListFilter):
    """Vyfiltruje obrazy, které ještě čekají na skutečný název."""

    title = 'název doplněn'
    parameter_name = 'has_real_title'

    def lookups(self, request, model_admin):
        return [('yes', 'Ano — má skutečný název'), ('no', 'Ne — zatím jen kód')]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(display_title='')
        if self.value() == 'no':
            return queryset.filter(display_title='')
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'slug', 'painting_count', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_painting_count=Count('paintings'))

    @admin.display(description='počet obrazů', ordering='_painting_count')
    def painting_count(self, obj):
        return obj._painting_count


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    # Název, kategorie, dostupnost i pořadí se dají přepsat přímo ve výpisu,
    # bez otevírání jednotlivých obrazů — u 90 děl to šetří stovky kliknutí.
    list_display = (
        'thumbnail_preview', 'code', 'display_title', 'category', 'availability', 'order',
    )
    list_display_links = ('thumbnail_preview', 'code')
    list_editable = ('display_title', 'category', 'availability', 'order')
    list_filter = ('category', 'availability', HasRealTitleFilter)
    search_fields = ('display_title', 'title', 'description')
    list_per_page = 50
    ordering = ('category', 'order')
    save_on_top = True
    readonly_fields = ('slug', 'large_preview', 'created_at', 'updated_at')

    fieldsets = (
        ('Obraz', {
            'fields': ('large_preview', 'image', 'title', 'display_title', 'slug', 'category'),
            'description': (
                'Kód obrazu je označení z autorova katalogu (např. K1) — '
                'zájemci ho uvádějí při poptávce, proto ho neměňte. '
                'Název obrazu vyplňte, jakmile je znám; dokud je prázdný, '
                'web zobrazuje „kategorie + kód“, tedy např. „Krajinomalba K1“.'
            ),
        }),
        ('Popis', {
            'fields': ('image_alt', 'description', 'description_en'),
            'description': (
                'Alt text popisuje obraz nevidomým návštěvníkům a vyhledávačům. '
                'Anglický popis je nepovinný — když zůstane prázdný, '
                'anglická verze webu ukáže český text s poznámkou.'
            ),
        }),
        ('Údaje o díle', {
            'fields': ('year', 'dimensions', 'technique'),
            'description': 'Nepovinné. Co nevíte, nechte prázdné — web daný řádek nezobrazí.',
        }),
        ('Dostupnost a řazení', {
            'fields': ('availability', 'order'),
            'description': (
                'Dostupnost: „K dispozici“ zobrazí u obrazu tlačítko „Mám zájem“. '
                '„Prodáno“ a „Neprodejné“ tlačítko skryjí. '
                'Pořadí určuje umístění v galerii — nižší číslo je dřív.'
            ),
        }),
        ('Systémové údaje', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Náhled')
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;object-fit:cover;'
                'border-radius:4px;border:1px solid #ded4c4;" />',
                obj.image.url,
            )
        return '—'

    @admin.display(description='Kód', ordering='title')
    def code(self, obj):
        return obj.title

    @admin.display(description='Náhled obrazu')
    def large_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:330px;height:auto;max-width:100%;'
                'border:1px solid #ded4c4;padding:8px;background:#fffdf9;" />',
                obj.image.url,
            )
        return 'Obrázek zatím nebyl nahrán.'
