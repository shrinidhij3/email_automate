from django.core.management.base import BaseCommand
from unread_emails.models import UnreadEmailAttachment
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update download URLs for all email attachments'

    def handle(self, *args, **options):
        # Get all attachments
        attachments = UnreadEmailAttachment.objects.all()
        total = attachments.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No attachments found in the database.'))
            return
            
        self.stdout.write(f'Found {total} attachments. Updating download URLs...')
        
        updated_count = 0
        for attachment in attachments:
            try:
                # Force update the download URL
                old_url = attachment.download_url
                attachment.download_url = attachment._generate_download_url()
                
                if attachment.download_url and attachment.download_url != old_url:
                    attachment.save(update_fields=['download_url'])
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated URL for attachment {attachment.id}: {attachment.download_url}'))
                
            except Exception as e:
                logger.error(f"Error updating URL for attachment {attachment.id}: {str(e)}")
                self.stdout.write(self.style.ERROR(f'Error updating attachment {attachment.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} out of {total} attachments'))
