# model
import os
import uuid
import base64
import logging
from django.db import models

# Set up logger
logger = logging.getLogger(__name__)
from django.core.validators import EmailValidator
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Generate a key from Django's SECRET_KEY
def get_fernet_key():
    salt = settings.SECRET_KEY[:16].encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
    return key

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'unread_emails/user_{instance.id}/{filename}'

class UnreadEmail(models.Model):
    """
    Model to store unread email form submissions with email provider configuration
    """
    PROVIDER_CHOICES = [
        ('gmail', 'Gmail'),
        ('other', 'Other'),
    ]
    
    # User information
    name = models.CharField(max_length=255, help_text="Full name of the submitter")
    email = models.EmailField(
        max_length=255,
        validators=[EmailValidator()],
        help_text="Email address of the submitter"
    )
    # Password field - stores encrypted password in the database
    _password = None
    password = models.CharField(
        max_length=1024,  # Increased to store encrypted data
        null=True,
        blank=True,
        help_text="Email account password (encrypted in database)"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store original password on init to detect changes
        self._password = self.password
    
    def save(self, *args, **kwargs):
        # Always encrypt the password if it's set and not already encrypted
        if self.password and not self.password.startswith('gAA'):  # Simple check if not encrypted
            try:
                f = Fernet(get_fernet_key())
                self.password = f.encrypt(self.password.encode()).decode()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error encrypting password: {e}")
                raise
        super().save(*args, **kwargs)
    
    def get_decrypted_password(self):
        """Get the decrypted password"""
        if not self.password:
            return None
        try:
            f = Fernet(get_fernet_key())
            return f.decrypt(self.password.encode()).decode()
        except Exception as e:
            logger.error(f"Error decrypting password: {e}")
            return None
    
    # Processing status
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether this submission has been processed"
    )
    
    # Provider information
    provider = models.CharField(
        max_length=100,  # Increased max_length to accommodate custom providers
        default='gmail',
        help_text="Email service provider (can be any value)"
    )
    
    # IMAP Configuration
    imap_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="IMAP server hostname"
    )
    imap_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="IMAP server port"
    )
    
    # SMTP Configuration
    smtp_host = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="SMTP server hostname"
    )
    smtp_port = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="SMTP server port"
    )
    
    # Security
    secure = models.BooleanField(
        default=True,
        help_text="Whether to use SSL/TLS for the connection (legacy field)"
    )
    use_ssl = models.BooleanField(
        default=True,
        help_text="Whether to use SSL/TLS for the connection (new field)"
    )
    
    # Timestamps and status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(
        default=False,
        help_text="Whether this submission has been processed"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Any additional notes or comments"
    )

    def __str__(self):
        return f"{self.name} <{self.email}>"

    class Meta:
        db_table = 'credentials_email'
        ordering = ['-created_at']
        verbose_name = 'Unread Email Submission'
        verbose_name_plural = 'Unread Email Submissions'


class UnreadEmailAttachment(models.Model):
    """
    Model to store file attachments for unread email submissions
    Files are stored directly in the database as binary data
    """
    def unread_email_attachment_path(instance, filename):
        """Generate file path for unread email attachments"""
        ext = os.path.splitext(filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        return os.path.join('unread_email_attachments', filename)

    unread_email = models.ForeignKey(
        UnreadEmail,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="The unread email submission this file belongs to"
    )
    file_data = models.BinaryField(
        null=True,
        blank=True,
        default=b'',
        help_text="The actual file data"
    )
    original_filename = models.CharField(
        max_length=255,
        help_text="Original name of the uploaded file"
    )
    content_type = models.CharField(
        max_length=100,
        help_text="MIME type of the file"
    )
    file_size = models.PositiveIntegerField(default=0, help_text="Size of the file in bytes")
    download_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct download URL for the file")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Unread Email Attachment'
        verbose_name_plural = 'Unread Email Attachments'

    def __str__(self):
        return f"{self.original_filename} ({self.unread_email.email})"

    def save_file(self, file):
        """
        Save file data to the model instance.
        
        Args:
            file: The uploaded file object
        """
        self.original_filename = file.name
        self.content_type = file.content_type or 'application/octet-stream'
        self.file_size = file.size
        
        # Read the file data and store it
        if hasattr(file, 'read'):
            self.file_data = file.read()
        elif hasattr(file, 'file') and hasattr(file.file, 'read'):
            self.file_data = file.file.read()
        else:
            raise ValueError("Invalid file object provided")
        
        # Generate download URL before saving
        self.download_url = self._generate_cloudflare_url()
        
        # Save the model with all fields
        self.save()
        
        # If download_url wasn't set, try to generate it again after save
        if not self.download_url:
            self.download_url = self._generate_download_url()
            if self.download_url:
                self.save(update_fields=['download_url'])
        
        return self
        
    def save(self, *args, **kwargs):
        """
        Save the model instance with proper handling for file uploads and Cloudflare URL generation.
        Uses transaction.atomic to ensure data consistency during concurrent uploads.
        """
        from django.db import transaction
        
        # If this is a new instance and file is being set
        is_new = self._state.adding
        
        # Use transaction to ensure atomicity
        with transaction.atomic():
            # Save the instance first to get an ID
            super().save(*args, **kwargs)
            
            # Generate Cloudflare URL after initial save
            if is_new and hasattr(self, 'file_data') and self.file_data and not self.download_url:
                self.download_url = self._generate_cloudflare_url()
                # Update only the download_url field
                if self.download_url:
                    UnreadEmailAttachment.objects.filter(pk=self.pk).update(
                        download_url=self.download_url
                    )
    
    def _generate_cloudflare_url(self):
        """
        Generate a Cloudflare R2 URL for the file.
        Returns None if Cloudflare is not configured.
        """
        if not hasattr(self, 'file_data') or not self.file_data:
            return None
            
        # Get Cloudflare configuration
        cloudflare_account_id = getattr(settings, 'CLOUDFLARE_ACCOUNT_ID', '')
        cloudflare_bucket_name = getattr(settings, 'CLOUDFLARE_BUCKET_NAME', '')
        
        if not cloudflare_account_id or not cloudflare_bucket_name:
            logger.warning("Cloudflare R2 configuration is missing in settings")
            return None
            
        try:
            # Generate a unique file name
            ext = os.path.splitext(self.original_filename)[1] if self.original_filename else '.bin'
            file_name = f"{uuid.uuid4()}{ext}"
            return f"https://{cloudflare_account_id}.r2.cloudflarestorage.com/{cloudflare_bucket_name}/{file_name}"
        except Exception as e:
            logger.error(f"Error generating Cloudflare URL: {str(e)}")
            return None

    def get_file_data(self):
        """
        Return file data for download
        """
        if not hasattr(self, 'file_data') or not self.file_data:
            return None
            
        try:
            # Return the binary data directly
            return bytes(self.file_data)
        except Exception as e:
            logger.error(f"Error reading file data: {str(e)}")
            return None
        
    def _generate_download_url(self):
        """Generate a download URL for this attachment."""
        from django.urls import reverse
        from django.conf import settings
        
        try:
            # Generate URL for the download endpoint
            # Note: Using the direct URL name without app namespace as it's included in the root URLs
            path = reverse('download-attachment', kwargs={'attachment_id': self.pk})
            
            # Use Cloudflare tunnel URL from settings, fallback to SITE_DOMAIN or localhost
            domain = getattr(settings, 'CLOUDFLARE_TUNNEL_URL', 
                          getattr(settings, 'SITE_DOMAIN', 'http://localhost:8000'))
            # Ensure domain doesn't end with a slash
            domain = domain.rstrip('/')
            
            # Ensure path starts with a slash
            if not path.startswith('/'):
                path = '/' + path
                
            full_url = f"{domain}{path}"
            logger.debug(f"Generated download URL: {full_url}")
            return full_url
        except Exception as e:
            logger.error(f"Error generating download URL: {e}")
            return ""
        
    def get_download_url(self):
        """Return the stored download URL."""
        if not self.download_url and self.pk:
            self.download_url = self._generate_download_url()
            self.save(update_fields=['download_url'])
        return self.download_url

    class Meta:
        db_table = 'unread_emails_unreademailattachment'
        ordering = ['-created_at']
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

