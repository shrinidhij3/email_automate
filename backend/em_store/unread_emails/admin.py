from django.contrib import admin
from .models import UnreadEmail, UnreadEmailAttachment

class UnreadEmailAttachmentInline(admin.TabularInline):
    model = UnreadEmailAttachment
    extra = 0
    fields = ('original_filename', 'content_type', 'file_size', 'created_at')
    readonly_fields = ('original_filename', 'content_type', 'file_size', 'created_at')
    show_change_link = True
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(UnreadEmail)
class UnreadEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'provider', 'created_at')
    list_filter = ('provider', 'created_at')
    search_fields = ('email', 'name', 'subject')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [UnreadEmailAttachmentInline]
    
    fieldsets = (
        ('Email Information', {
            'fields': ('name', 'email', 'subject', 'body')
        }),
        ('Server Configuration', {
            'fields': ('provider', 'imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'secure', 'use_ssl'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UnreadEmailAttachment)
class UnreadEmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'content_type', 'file_size', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('original_filename', 'unread_email__email', 'unread_email__name')
    readonly_fields = ('original_filename', 'content_type', 'file_size', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
