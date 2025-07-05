from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the current sequence value for campaigns_campaignemailattachment'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get current max ID
            cursor.execute("SELECT MAX(id) FROM campaigns_campaignemailattachment;")
            max_id = cursor.fetchone()[0] or 0
            
            # Get current sequence value
            cursor.execute("SELECT last_value FROM campaigns_campaignemailattachment_id_seq;")
            last_value = cursor.fetchone()[0] or 0
            
            # Get next sequence value (without consuming it)
            cursor.execute("SELECT nextval('campaigns_campaignemailattachment_id_seq');")
            next_val = cursor.fetchone()[0]
            # Rollback the nextval so we don't consume it
            cursor.execute("SELECT setval('campaigns_campaignemailattachment_id_seq', %s, false);", [last_value])
            
            self.stdout.write(self.style.SUCCESS(f"Current max ID in table: {max_id}"))
            self.stdout.write(self.style.SUCCESS(f"Current sequence last value: {last_value}"))
            self.stdout.write(self.style.SUCCESS(f"Next sequence value would be: {next_val}"))
            
            if last_value <= max_id:
                self.stdout.write(self.style.ERROR("\nWARNING: Sequence is behind or equal to max ID! This will cause duplicate key errors!"))
                self.stdout.write(self.style.ERROR(f"Current max ID: {max_id}"))
                self.stdout.write(self.style.ERROR(f"Next sequence value: {next_val}"))
            else:
                self.stdout.write(self.style.SUCCESS("\nSequence is properly set (last_value > max_id)"))
