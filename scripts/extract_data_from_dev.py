"""
# extract_data_from_dev.py

## Purpose:
This script extracts records from the DEV database that are candidates for transfer to the PROD database.

## Usage:
This script is designed to be used internally by `data_transfer.py` and typically does not need to be run directly.

## Details:
- Queries the DEV database for new or updated records in the `documents` table.
- Returns the extracted records for further processing.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_new_records():
    try:
        # Connect to the DEV database
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_DEV_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        
        with conn.cursor() as cursor:
            # Extract all records from the documents table
            cursor.execute("""
                SELECT id, company_id, title, content
                FROM documents;
            """)
            new_records = cursor.fetchall()
            return new_records

    except Exception as e:
        print(f"Error extracting new records: {e}")
        return []
    finally:
        conn.close()
