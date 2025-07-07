from django.core.management.base import BaseCommand
from campaigns.models import CampaignEmailAttachment

class Command(BaseCommand):
    help = 'Update download URLs for all attachments to use the Render URL'

    def handle(self, *args, **options):
        updated = 0
        for attachment in CampaignEmailAttachment.objects.all():
            old_url = attachment.download_url
            attachment.download_url = attachment._generate_download_url()
            if old_url != attachment.download_url:
                attachment.save(update_fields=['download_url'])
                updated += 1
                self.stdout.write(f'Updated {attachment.original_filename}: {attachment.download_url}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} attachment URLs'))
