from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import EmailCampaign, CampaignEmailAttachment

User = get_user_model()

class CampaignEmailAttachmentInline(admin.TabularInline):
    model = CampaignEmailAttachment
    fk_name = 'email_campaign'  # Specify which foreign key to use
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
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # If password is being set (not just the placeholder)
        if password and password != '********':
            return password
        # If password is not being changed, return the existing value
        if self.instance and self.instance.pk:
            return self.instance.password
        return password
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # If password is being set (not just the placeholder)
        if password and password != '********':
            return password
        # If password is not being changed, return the existing value
        if self.instance and self.instance.pk:
            return self.instance.password
        return password


class CampaignResource(resources.ModelResource):
    created_by = fields.Field(
        column_name='created_by',
        attribute='created_by',
        widget=ForeignKeyWidget(User, 'username')
    )

    class Meta:
        model = EmailCampaign
        fields = (
            'id', 'name', 'email', 'provider', 'subject', 'body',
            'imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'use_ssl',
            'created_by', 'created_at', 'updated_at', 'notes'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = False
        exclude = ('id', 'password')
        import_id_fields = ('email',)


@admin.register(EmailCampaign)
class EmailCampaignAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    form = EmailCampaignForm
    resource_class = CampaignResource
    list_display = (
        'name', 'email', 'provider', 'created_by', 'created_at', 'updated_at'
    )
    list_filter = ('provider', 'created_at')
    search_fields = ('name', 'email', 'subject', 'body')
    readonly_fields = (
        'created_at', 'updated_at', 'get_decrypted_password_display', 
        'preview_attachments', 'created_by'
    )
    date_hierarchy = 'created_at'
    inlines = [CampaignEmailAttachmentInline]
    actions = ['export_selected']
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('name', 'subject', 'body', 'notes')
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
            'fields': (
                ('created_at', 'updated_at'),
                'created_by'
            ),
            'classes': ('collapse',)
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
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('campaigns.can_manage_all_campaigns'):
            return qs
        return qs.filter(created_by=request.user)
        
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
    @admin.action(description='Export selected campaigns')
    def export_selected(self, request, queryset):
        # This will use django-import-export's export action
        pass

class CampaignEmailAttachmentResource(resources.ModelResource):
    email_campaign = fields.Field(
        column_name='email_campaign',
        attribute='email_campaign',
        widget=ForeignKeyWidget(EmailCampaign, 'name')
    )
    
    class Meta:
        model = CampaignEmailAttachment
        fields = (
            'id', 'original_filename', 'content_type', 'file_size',
            'email_campaign', 'created_at', 'updated_at'
        )
        export_order = fields
        skip_unchanged = True
        report_skipped = False
        exclude = ('id', 'file')


@admin.register(CampaignEmailAttachment)
class CampaignEmailAttachmentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = CampaignEmailAttachmentResource
    list_display = (
        'original_filename', 'get_campaign_name', 'content_type', 
        'get_file_size_display', 'created_at', 'download_link'
    )
    list_filter = ('content_type', 'created_at', 'email_campaign__provider')
    search_fields = ('original_filename', 'email_campaign__name', 'email_campaign__email')
    readonly_fields = (
        'original_filename', 'content_type', 'file_size', 
        'created_at', 'updated_at', 'file_preview', 'download_link'
    )
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('campaigns.can_manage_all_campaigns'):
            return qs
        return qs.filter(email_campaign__created_by=request.user)
    
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
