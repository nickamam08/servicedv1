import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME")
    )
    print("SUCCESS: Connected to the database.")
    cur = conn.cursor()
    cur.execute("SELECT 1")
    print("SUCCESS: Executed SELECT 1.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
