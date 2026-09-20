from django.contrib import admin

from .models import ContactMessage, Exhibition, ExternalLink, PressMention


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Exhibition)
class ExhibitionAdmin(admin.ModelAdmin):
    list_display = ('title', 'place', 'year', 'order')
    list_editable = ('order',)
    ordering = ('-year', 'order')
    search_fields = ('title', 'place')
    fields = ('title', 'place', 'year', 'description', 'description_en', 'order')


@admin.register(PressMention)
class PressMentionAdmin(admin.ModelAdmin):
    list_display = ('source', 'kind', 'date', 'order')
    list_filter = ('kind',)
    ordering = ('kind', 'order')
    search_fields = ('source', 'text')
    fields = ('kind', 'source', 'text', 'text_en', 'link', 'date', 'order')


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order')
    ordering = ('order',)
