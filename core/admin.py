import re

from django.contrib import admin
from django.utils.html import format_html

from .models import ContactMessage, Exhibition, ExternalLink, PressMention


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Schránka zpráv z kontaktního formuláře — jen ke čtení a odbavení."""

    list_display = ('status', 'name', 'email', 'short_message', 'painting_code', 'created_at', 'is_read')
    list_display_links = ('name',)
    list_editable = ('is_read',)
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 50
    readonly_fields = ('name', 'email', 'message', 'created_at', 'painting_code')

    fieldsets = (
        ('Odesílatel', {'fields': ('name', 'email', 'created_at')}),
        ('Zpráva', {
            'fields': ('painting_code', 'message'),
            'description': 'Text přišel z formuláře na webu, proto ho nelze upravovat.',
        }),
        ('Vyřízení', {
            'fields': ('is_read',),
            'description': 'Zaškrtněte, jakmile je zpráva vyřízená — zmizí z nepřečtených.',
        }),
    )

    @admin.display(description='')
    def status(self, obj):
        """Barevná tečka, ať je nepřečtená zpráva vidět na první pohled."""
        colour = '#ded4c4' if obj.is_read else '#b08d57'
        label = 'přečteno' if obj.is_read else 'nepřečteno'
        return format_html(
            '<span title="{}" style="display:inline-block;width:10px;height:10px;'
            'border-radius:50%;background:{};"></span>', label, colour,
        )

    @admin.display(description='Zpráva')
    def short_message(self, obj):
        text = obj.message.replace('\n', ' ')
        return text[:60] + ('…' if len(text) > 60 else '')

    @admin.display(description='Kód obrazu')
    def painting_code(self, obj):
        """Kód díla vytažený ze zprávy — poptávky ho uvádějí v uvozovkách."""
        match = re.search(r'[„"]([A-Za-z]{1,3}\d{1,3})[“"]', obj.message)
        if match:
            return match.group(1)
        return '—'

    def has_add_permission(self, request):
        return False  # zprávy vznikají jen odesláním formuláře na webu


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'place', 'order')
    list_editable = ('order',)
    list_filter = ('place',)
    search_fields = ('title', 'place', 'year')
    ordering = ('-year', 'order')
    list_per_page = 50

    fieldsets = (
        (None, {
            'fields': ('year', 'title', 'place'),
            'description': (
                'Název je místo konání či název výstavy, „místo“ slouží jako '
                'skupina, pod kterou se výstava na webu zařadí '
                '(např. „Účast na výstavách v České republice“).'
            ),
        }),
        ('Popis', {
            'fields': ('description', 'description_en'),
            'description': 'Nepovinné. Anglický popis prázdný = zobrazí se český.',
        }),
        ('Řazení', {'fields': ('order',)}),
    )


@admin.register(PressMention)
class PressMentionAdmin(admin.ModelAdmin):
    list_display = ('source', 'kind', 'short_text', 'date', 'order')
    list_editable = ('order',)
    list_filter = ('kind',)
    search_fields = ('source', 'text')
    ordering = ('kind', 'order')
    list_per_page = 50

    fieldsets = (
        (None, {
            'fields': ('kind', 'source', 'date', 'link'),
            'description': (
                'Druh „Citát“ se na webu zobrazí jako výrok s uvedením autora, '
                '„Publikace“ jako položka bibliografie.'
            ),
        }),
        ('Text', {
            'fields': ('text', 'text_en'),
            'description': (
                'Citáty se nepřekládají strojově. Anglický text doplňte ručně, '
                'jinak se i v anglické verzi zobrazí český originál.'
            ),
        }),
        ('Řazení', {'fields': ('order',)}),
    )

    @admin.display(description='Text')
    def short_text(self, obj):
        text = obj.text.replace('\n', ' ')
        return text[:70] + ('…' if len(text) > 70 else '')


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'url', 'order')
    list_editable = ('icon', 'order')
    list_filter = ('icon',)
    search_fields = ('title', 'url')
    ordering = ('order',)
