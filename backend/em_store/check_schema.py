import django
import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_table_schema():
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'credentials_email';
        """)
        
        print("Current schema for credentials_email table:")
        for row in cursor.fetchall():
            print(f"{row[0]}: {row[1]} (Nullable: {row[2]})")
        
        # Check if our new fields exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'credentials_email' 
            AND column_name IN ('imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'provider', 'secure');
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        print("\nChecking for new fields:")
        for field in ['imap_host', 'imap_port', 'smtp_host', 'smtp_port', 'provider', 'secure']:
            status = "✓" if field in existing_columns else "✗"
            print(f"{status} {field}")

if __name__ == "__main__":
    check_table_schema()
