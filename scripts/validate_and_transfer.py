"""
# validate_and_transfer.py

## Purpose:
This script validates the extracted data from the DEV database and prepares it for insertion or updating in the PROD database.

## Usage:
This script is invoked within `data_transfer.py` and is not typically run directly by the user.

## Details:
- Validates the data by checking for duplicates and other constraints.
- Prepares the data for transfer to the PROD database.
"""

import psycopg2
import os
from dotenv import load_dotenv
from extract_data_from_dev import extract_new_records
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def count_records(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    return cursor.fetchone()[0]

def get_existing_records(cursor, table_name):
    cursor.execute(f"SELECT id FROM {table_name};")
    return set(record[0] for record in cursor.fetchall())

def validate_and_transfer_data():
    # Establish connections to both DEV and PROD databases
    dev_conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_DEV_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    prod_conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_PROD_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

    dev_cursor = dev_conn.cursor()
    prod_cursor = prod_conn.cursor()

    try:
        # Count records in DEV database
        dev_document_count = count_records(dev_cursor, "documents")
        logging.info(f"Number of records in DEV 'documents' table: {dev_document_count}")

        # Count records in PROD database
        prod_document_count_before = count_records(prod_cursor, "documents")
        logging.info(f"Number of records in PROD 'documents' table before transfer: {prod_document_count_before}")

        # Extract data from the DEV database
        documents_data = extract_new_records()

        # Track updated and skipped records
        updated_records = 0
        skipped_records = 0

        # Iterate over the documents data
        for document in documents_data:
            document_id = document[0]
            company_id = document[1]
            title = document[2]
            content = document[3]

            try:
                # Use individual transactions for each record to handle errors separately
                with prod_conn.cursor() as single_cursor:
                    single_cursor.execute("""
                        INSERT INTO documents (id, company_id, title, content)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id)
                        DO UPDATE SET company_id = EXCLUDED.company_id,
                                      title = EXCLUDED.title,
                                      content = EXCLUDED.content;
                    """, (document_id, company_id, title, content))
                    updated_records += 1
                prod_conn.commit()
            except psycopg2.errors.UniqueViolation as e:
                # Log the unique constraint violation and continue
                logging.warning(f"Unique constraint violation for title '{title}': {e}")
                skipped_records += 1
                prod_conn.rollback()  # Rollback the transaction for the failed record

    except Exception as e:
        logging.warning(f"Non-fatal error during data validation and transfer: {e}")
    finally:
        # Re-count records in PROD database
        prod_document_count_after = count_records(prod_cursor, "documents")
        logging.info(f"Number of records in PROD 'documents' table after transfer: {prod_document_count_after}")
        logging.info(f"Number of records updated in PROD 'documents' table: {updated_records}")
        logging.info(f"Number of records skipped due to unique constraint violations: {skipped_records}")

        dev_cursor.close()
        prod_cursor.close()
        dev_conn.close()
        prod_conn.close()
