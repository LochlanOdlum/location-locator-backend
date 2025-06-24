from dotenv import load_dotenv
import os
import time
import psycopg2
import pandas as pd
from psycopg2 import OperationalError

load_dotenv()

script_dir = os.path.dirname(os.path.abspath(__file__))
seeds_dir = os.path.join(script_dir, 'table_seeds') 

# Construct the database URL from individual parts
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Order of tables in which they can be created (FKs must be created first)
table_dependency_order = ["users", "addresses", "homes", "locations", "distances"]


# We’ll truncate in reverse so children go before parents
def clear_tables(conn):
    cursor = conn.cursor()
    # Use TRUNCATE RESTART IDENTITY CASCADE to wipe and reset serials
    for table in reversed(table_dependency_order):
        cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
        print(f"Truncated {table}")
    conn.commit()

def insert_csv_into_table(csv_path, table_name, conn):
    df = pd.read_csv(csv_path)

    cursor = conn.cursor()

    # Generate a query to insert data
    columns = ', '.join(df.columns)
    placeholders = ', '.join(['%s'] * len(df.columns))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Insert data row by row
    for row in df.itertuples(index=False, name=None):
        cursor.execute(query, row)

    conn.commit()
    print(f"Inserted data into {table_name}")

    # Update serial sequence (optional, but helps keep `id` in sync)
    cursor.execute(f"SELECT setval('{table_name}_id_seq', (SELECT MAX(id) FROM {table_name}));")
    print("Updated incremental counter")

def database_is_seeded(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    return user_count > 0

def main():
    conn = None

    # Retry loop to wait for the DB to be ready
    for attempt in range(10):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break  # Success
        except OperationalError:
            print(f"Database not ready (attempt {attempt + 1}/10), retrying in 1s...")
            time.sleep(1)
    else:
        print("Database not reachable after 10 attempts. Exiting.")
        return

    try:

        clear_tables(conn)
        
        if database_is_seeded(conn):
            print("Database already seeded. Skipping.")
            return

        for table_name in table_dependency_order:
            csv_path = os.path.join(seeds_dir, table_name + ".csv")
            insert_csv_into_table(csv_path, table_name, conn)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
