from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import EmailCampaign, CampaignEmailAttachment

class CampaignEmailAttachmentInline(admin.TabularInline):
    model = CampaignEmailAttachment
    extra = 0
    fields = ('file', 'original_filename', 'content_type', 'file_size', 'created_at')
    readonly_fields = ('original_filename', 'content_type', 'file_size', 'created_at')
    show_change_link = True
    
    def has_change_permission(self, request, obj=None):
        return False

class EmailCampaignForm(forms.ModelForm):
    class Meta:
        model = EmailCampaign
        fields = '__all__'
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # If password is being set (not just the placeholder)
        if password and password != '********':
            return password
        # If password is not being changed, return the existing value
        if self.instance and self.instance.pk:
            return self.instance.password
        return password

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    form = EmailCampaignForm
    list_display = (
        'name', 'email', 'provider', 'created_by', 'created_at'
    )
    list_filter = ('provider', 'created_at')
    search_fields = ('name', 'email', 'subject', 'body')
    readonly_fields = (
        'created_at', 'updated_at', 
        'get_decrypted_password_display', 'preview_attachments'
    )
    date_hierarchy = 'created_at'
    inlines = [CampaignEmailAttachmentInline]
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'subject', 'body', 'status', 'notes')
        }),
        ('Email Account', {
            'fields': ('email', 'password', 'get_decrypted_password_display', 'provider')
        }),
        ('Server Configuration', {
            'fields': (
                ('imap_host', 'imap_port'),
                ('smtp_host', 'smtp_port'),
                'use_ssl',
            ),
            'classes': ('collapse',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        }),
        ('Attachments', {
            'fields': ('preview_attachments',),
            'classes': ('collapse',)
        }),
    )
    
    def get_decrypted_password_display(self, obj):
        if obj.password:
            return '********'  # Show masked password in admin
        return 'Not set'
    get_decrypted_password_display.short_description = 'Password (encrypted)'
    
    def preview_attachments(self, obj):
        attachments = obj.attachments.all()
        if not attachments:
            return 'No attachments'
        
        links = []
        for attachment in attachments:
            url = reverse('admin:campaigns_campaignemailattachment_change', args=[attachment.id])
            links.append(f'<li><a href="{url}" target="_blank">{attachment.original_filename}</a> ({attachment.get_file_size_display()})</li>')
        
        return mark_safe(f'<ul>{"".join(links)}</ul>')
    preview_attachments.short_description = 'Attachments'
    preview_attachments.allow_tags = True
    
    def save_model(self, request, obj, form, change):
        # Only set created_by if this is a new object
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(CampaignEmailAttachment)
class CampaignEmailAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 'get_campaign_name', 'content_type', 
        'get_file_size_display', 'created_at', 'download_link'
    )
    list_filter = ('content_type', 'created_at', 'email_campaign__provider')
    search_fields = ('original_filename', 'email_campaign__name', 'email_campaign__email')
    readonly_fields = (
        'original_filename', 'content_type', 'file_size', 
        'created_at', 'updated_at', 'file_preview'
    )
    date_hierarchy = 'created_at'
    
    def get_campaign_name(self, obj):
        return obj.email_campaign.name
    get_campaign_name.short_description = 'Campaign'
    get_campaign_name.admin_order_field = 'email_campaign__name'
    
    def download_link(self, obj):
        return format_html(
            '<a class="button" href="{}" download>Download</a>',
            obj.file.url if obj.file else '#'
        )
    download_link.short_description = 'Download'
    download_link.allow_tags = True
    
    def get_file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} bytes"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "-"
    get_file_size_display.short_description = 'File Size'
    get_file_size_display.admin_order_field = 'file_size'

    def file_preview(self, obj):
        if obj.file and obj.content_type.startswith('image/'):
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.file.url
            )
        return 'Preview not available'
    file_preview.short_description = 'Preview'
    file_preview.allow_tags = True
