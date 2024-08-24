import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


try:
    conn = psycopg2.connect(host=HOST, dbname="postgres", user=USER, password=PASSWORD)
    print("Connection successful")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
