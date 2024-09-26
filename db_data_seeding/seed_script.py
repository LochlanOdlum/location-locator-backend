from dotenv import load_dotenv

load_dotenv()

import os
import psycopg2
import pandas as pd

DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ENDPOINT = os.getenv("DATABASE_ENDPOINT")

# Order of tables in which they can be created (FK's must be created first)
table_dependency_order = ["users", "addresses", "homes", "locations", "distances"]

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

    cursor.execute(f"SELECT setval('{table_name}_id_seq', (SELECT MAX(id) FROM {table_name}));")
    print("Updated incremental counter")

def main():
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname="locationlocator",
        user=DATABASE_USERNAME,
        password=DATABASE_PASSWORD,
        host=DATABASE_ENDPOINT,
        port=5432
    )

    try:
        # Directory containing the CSV files
        seeds_dir = './table_seeds'

        # Order of tables is important here. Must define foreign keys first
        for table_name in ["users", "addresses", "homes", "locations", "distances"]:
            # Get the full path of the CSV file
            csv_path = os.path.join(seeds_dir, table_name + ".csv")

            insert_csv_into_table(csv_path, table_name, conn)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

