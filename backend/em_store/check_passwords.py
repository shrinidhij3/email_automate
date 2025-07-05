import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
django.setup()

from django.db import connection

def check_database_passwords():
    """Check the state of passwords in the database"""
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'unread_emails_unreademail';
        """)
        columns = cursor.fetchall()
        print("\nTable columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Check if we have any data
        cursor.execute("SELECT COUNT(*) FROM unread_emails_unreademail;")
        count = cursor.fetchone()[0]
        print(f"\nTotal records: {count}")
        
        if count > 0:
            # Show first few records
            cursor.execute("""
                SELECT id, email, 
                       CASE 
                           WHEN password IS NULL THEN 'NULL' 
                           WHEN password = '' THEN 'EMPTY' 
                           WHEN password LIKE 'gAA%' THEN 'ENCRYPTED' 
                           ELSE 'PLAINTEXT' 
                       END as password_status,
                       LENGTH(password) as password_length
                FROM unread_emails_unreademail
                ORDER BY id DESC
                LIMIT 5;
            """)
            print("\nRecent records:")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}, Email: {row[1]}, Password: {row[2]} (Length: {row[3] if row[3] is not None else 'N/A'})")

if __name__ == "__main__":
    check_database_passwords()
