from dotenv import load_dotenv

load_dotenv()

import psycopg2
import os


DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_ENDPOINT = os.getenv("DATABASE_ENDPOINT")

# Order of tables in which they can be created (FK's must be created first)
table_dependency_order = ["users", "addresses", "homes", "locations", "distances"]

def main():

  conn = psycopg2.connect(
    dbname="locationlocator",
    user=DATABASE_USERNAME,
    password=DATABASE_PASSWORD,
    host=DATABASE_ENDPOINT,
    port=5432
  )

  try:
    cursor = conn.cursor()  
    print("t")
    print(table_dependency_order)

    for table in reversed(table_dependency_order):
        print(table)
        cursor.execute(f"DROP TABLE {table}")

    conn.commit()
  except Exception as e:
    print(f"Error: {e}")

  finally:
    conn.close()


if __name__ == "__main__":
    main()