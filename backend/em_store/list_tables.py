import os
import django

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
    django.setup()

def list_tables():
    from django.db import connection
    with connection.cursor() as cursor:
        # For PostgreSQL
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cursor.fetchall()
        print("\nDatabase Tables:")
        print("-" * 30)
        for table in tables:
            print(table[0])
        print("-" * 30)

if __name__ == "__main__":
    setup_django()
    list_tables()
