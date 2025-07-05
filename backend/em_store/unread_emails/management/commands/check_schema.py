from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check the database schema for the unread_emails app'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if the table exists
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'credentials_email';
            """)
            
            self.stdout.write(self.style.SUCCESS('Current schema for credentials_email table:'))
            for row in cursor.fetchall():
                self.stdout.write(f"{row[0]}: {row[1]} (Nullable: {row[2]})")
            
            # Check if our new fields exist
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'credentials_email' 
                AND column_name IN ('imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'provider', 'secure');
            """)
            
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write("\nChecking for new fields:")
            for field in ['imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'provider', 'secure']:
                status = "✓" if field in existing_columns else "✗"
                self.stdout.write(f"{status} {field}")
        
        self.stdout.write("\nTo fix any missing fields, try:")
        self.stdout.write("1. python manage.py migrate unread_emails 0005_add_email_config_fields --fake")
        self.stdout.write("2. python manage.py migrate unread_emails")
