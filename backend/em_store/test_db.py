import os
import django
from django.db import connection

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'em_store.settings')
    django.setup()

def test_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("Database connection successful!")
            print(f"Test query result: {result}")
            
            # List all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = cursor.fetchall()
            
            if tables:
                print("\nDatabase Tables:")
                print("-" * 30)
                for table in tables:
                    print(table[0])
            else:
                print("\nNo tables found in the database.")
            
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    setup_django()
    test_connection()
