import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_table_structure():
    with connection.cursor() as cursor:
        # Get table columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'unread_emails_unreademailattachment';
        """)
        print("\nTable: unread_emails_unreademailattachment")
        print("-" * 50)
        print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default'}")
        print("-" * 70)
        for col in cursor.fetchall():
            print(f"{col[0]:<30} {col[1]:<20} {col[2]:<10} {col[3] or 'None'}")

if __name__ == "__main__":
    check_table_structure()
