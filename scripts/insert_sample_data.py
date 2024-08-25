"""
# insert_sample_data.py

## Purpose:
This script inserts sample data into the DEV and PROD databases using JSON files located in the `sample_data` directory.

## Usage:
    python3 scripts/insert_sample_data.py
"""

import json
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def load_json(filename):
    """Load JSON data from a file."""
    try:
        # Construct the full file path
        script_dir = os.path.dirname(__file__)
        file_path = os.path.join(script_dir, '..', 'sample_data', filename)
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file: {file_path}")
        raise

def insert_data(db_name, data):
    """Insert data into the specified database and count records."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=db_name,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    try:
        with conn.cursor() as cursor:
            for table, rows in data.items():
                # Clear existing data
                cursor.execute(f"DELETE FROM {table};")
                # Insert new data
                for row in rows:
                    columns = ', '.join(row.keys())
                    values = ', '.join(f"%s" for _ in row)
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({values});"
                    cursor.execute(sql, tuple(row.values()))
            
            conn.commit()
            print(f"Data inserted into {db_name} successfully.")
            
            # Count and display the number of records in each table
            print(f"Counting records in tables of {db_name}...")
            for table in data.keys():
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"Table '{table}' has {count} records.")
                
    except Exception as e:
        print(f"Error inserting data into {db_name}: {e}")
    finally:
        conn.close()

def main():
    # Load sample data
    dev_data = load_json('dev_sample_data.json')
    prod_data = load_json('prod_sample_data.json')
    
    # Insert sample data into DEV and PROD databases
    print("Inserting sample data into DEV database...")
    insert_data(os.getenv("DB_DEV_NAME"), dev_data)
    
    print("Inserting sample data into PROD database...")
    insert_data(os.getenv("DB_PROD_NAME"), prod_data)

if __name__ == "__main__":
    main()

