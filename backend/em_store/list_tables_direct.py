import psycopg2
from dotenv import load_dotenv
import os

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get database connection parameters from environment variables
    db_params = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }
    
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Query to get all tables in the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        # Fetch all tables
        tables = cursor.fetchall()
        
        # Print the results
        if tables:
            print("\nAvailable tables in the database:")
            print("-" * 40)
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found in the public schema.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        if 'conn' in locals():
            cursor.close()
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
