from django.contrib import admin
from .models import EmailEntry


@admin.register(EmailEntry)
class EmailEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing EmailEntry instances.
    """
    list_display = ('email', 'name', 'client_email', 'date_of_signup', 'unsubscribe', 'day_one', 'day_two', 'day_four')
    list_filter = ('date_of_signup', 'unsubscribe')
    search_fields = ('email', 'name', 'client_email')
    readonly_fields = ('date_of_signup',)
    date_hierarchy = 'date_of_signup'
    list_per_page = 25
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('name', 'email', 'client_email', 'unsubscribe')
        }),
        ('Email Tracking', {
            'fields': (
                'day_one',
                'day_two',
                'day_four',
                'day_five',
                'day_seven',
                'day_nine'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('date_of_signup',),
            'classes': ('collapse',)
        }),
    )
