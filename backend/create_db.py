import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to the default 'postgres' database to create the new one
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE smartcook;")
    print("Database 'smartcook' created successfully!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
