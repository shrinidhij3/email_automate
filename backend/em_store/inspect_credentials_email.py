import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
    django.setup()

def inspect_credentials_email():
    from django.db import connection
    with connection.cursor() as cursor:
        # PostgreSQL query to get column information
        cursor.execute("""
            SELECT 
                ordinal_position as cid,
                column_name as name,
                data_type as type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = 'credentials_email';
        """)
        columns = cursor.fetchall()
        
        print("\nColumns in credentials_email table:")
        print("-" * 80)
        print(f"{'CID':<5} {'Name':<20} {'Type':<30} {'Nullable':<10} {'Default'}")
        print("-" * 80)
        for col in columns:
            cid, name, col_type, is_nullable, default = col
            print(f"{cid:<5} {name:<20} {col_type:<30} {'NO' if is_nullable == 'NO' else 'YES':<10} {default if default else 'NULL'}")

if __name__ == "__main__":
    setup_django()
    inspect_credentials_email()
