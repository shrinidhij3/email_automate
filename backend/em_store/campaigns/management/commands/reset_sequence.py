from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reset the database sequence for the CampaignEmailAttachment model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get the max ID from the table
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            
            # Set the sequence to the next available ID
            cursor.execute(f"ALTER SEQUENCE campaigns_campaignemailattachment_id_seq RESTART WITH {max_id + 1};")
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset sequence to {max_id + 1}')
            )
