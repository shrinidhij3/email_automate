import psycopg2
from dotenv import load_dotenv
import os

def get_table_columns(table_name):
    load_dotenv()
    
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    
    try:
        with conn.cursor() as cur:
            # Get column information
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            print(f"\nStructure of table '{table_name}':")
            print("-" * 60)
            print(f"{'Column Name':<30} {'Data Type':<20} {'Nullable':<10} {'Default'}")
            print("-" * 60)
            
            for col in cur.fetchall():
                column_name, data_type, is_nullable, column_default = col
                print(f"{column_name:<30} {data_type:<20} {is_nullable:<10} {column_default}")
                
    finally:
        conn.close()

if __name__ == "__main__":
    get_table_columns('email_auto')
