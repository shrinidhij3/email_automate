from django.db import models
from django.core.validators import EmailValidator
from campaigns.models import EmailCampaign

class EmailEntry(models.Model):
    """
    Model to store email entries from the submission form.
    Maps to the existing email_auto table in the database.
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField(
        help_text="Full name of the subscriber"
    )
    
    email = models.TextField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address of the subscriber"
    )
    
    client_email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Email address of the client who added this entry"
    )
    
    date_of_signup = models.DateField(
        auto_now_add=True,
        help_text="Date when the user signed up"
    )
    
    # Email tracking fields
    day_one = models.TextField(
        null=True,
        blank=True,
        help_text="Day one email status"
    )
    
    day_two = models.TextField(
        null=True,
        blank=True,
        help_text="Day two email status"
    )
    
    day_four = models.TextField(
        null=True,
        blank=True,
        help_text="Day four email status"
    )
    
    day_five = models.TextField(
        null=True,
        blank=True,
        help_text="Day five email status"
    )
    
    day_seven = models.TextField(
        null=True,
        blank=True,
        help_text="Day seven email status"
    )
    
    day_nine = models.TextField(
        null=True,
        blank=True,
        help_text="Day nine email status"
    )
    
    unsubscribe = models.BooleanField(
        default=False,
        help_text="Whether the user has unsubscribed from emails"
    )

    campaign = models.ForeignKey(
        EmailCampaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_entries',
        help_text="The campaign this email entry is associated with"
    )
    
    class Meta:
        db_table = 'email_auto'  # Connect to existing table
        verbose_name = "Email Entry"
        verbose_name_plural = "Email Entries"
        ordering = ['date_of_signup', 'id']  # Oldest first, then by ID for consistent ordering
    
    def __str__(self):
        return f"{self.name} <{self.email}>"
