import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# PostgreSQL connection
conn = psycopg2.connect(
    user='postgres',
    password='postgres',  # Change to your password
    host='localhost',
    port='5432',
    database='postgres'
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Drop and recreate database
try:
    cursor.execute("DROP DATABASE IF EXISTS pharma_db;")
    print("✓ Old database dropped")
    cursor.execute("CREATE DATABASE pharma_db;")
    print("✓ New database created")
except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()

print("\nNow run:")
print("python manage.py migrate")
print("python manage.py loaddata datadump.json")
