from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Painting


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


class HasRealTitleFilter(admin.SimpleListFilter):
    """Umožní vyfiltrovat obrazy, které ještě čekají na skutečný název."""

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


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    # display_title je list_editable, aby šlo názvy doplňovat hromadně
    # přímo ve výpisu — obraz po obrazu, bez otevírání detailu.
    list_display = ('thumbnail', 'title', 'display_title', 'category', 'year', 'availability', 'order')
    list_display_links = ('thumbnail', 'title')
    list_editable = ('display_title', 'year', 'availability', 'order')
    list_filter = ('category', 'availability', HasRealTitleFilter)
    search_fields = ('title', 'display_title', 'description')
    ordering = ('category', 'order')
    list_per_page = 30
    readonly_fields = ('slug', 'preview')
    fieldsets = (
        (None, {
            'fields': ('title', 'display_title', 'slug', 'category', 'image', 'preview', 'image_alt')
        }),
        ('Popis', {
            'fields': ('description', 'description_en')
        }),
        ('Detaily obrazu', {
            'fields': ('year', 'dimensions', 'technique')
        }),
        ('Dostupnost a řazení', {
            'fields': ('availability', 'order')
        }),
    )

    @admin.display(description='náhled')
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:56px;width:56px;object-fit:cover;'
                'border-radius:3px;border:1px solid #ddd;" />', obj.image.url
            )
        return '—'

    @admin.display(description='náhled obrazu')
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:320px;height:auto;" />', obj.image.url)
        return '—'

