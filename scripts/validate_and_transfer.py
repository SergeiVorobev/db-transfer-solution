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

        # Get existing records in PROD database
        existing_ids_in_prod = get_existing_records(prod_cursor, "documents")

        # Extract data from the DEV database
        documents_data = extract_new_records()

        # Track updated records
        updated_records = 0

        # Iterate over the documents data
        for document in documents_data:
            document_id = document[0]
            company_id = document[1]
            title = document[2]
            content = document[3]

            if document_id in existing_ids_in_prod:
                updated_records += 1

            try:
                # Insert or update the document in the PROD database
                prod_cursor.execute("""
                    INSERT INTO documents (id, company_id, title, content)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (id)
                    DO UPDATE SET company_id = EXCLUDED.company_id,
                                  title = EXCLUDED.title,
                                  content = EXCLUDED.content;
                """, (document_id, company_id, title, content))
            except psycopg2.errors.UniqueViolation as e:
                # Handle unique constraint violation (e.g., log and continue)
                logging.warning(f"Unique constraint violation during insert/update: {e}")
                continue

        # Commit the transaction
        prod_conn.commit()

        # Re-count records in PROD database
        prod_document_count_after = count_records(prod_cursor, "documents")
        logging.info(f"Number of records in PROD 'documents' table after transfer: {prod_document_count_after}")
        logging.info(f"Number of records updated in PROD 'documents' table: {updated_records}")

    except Exception as e:
        logging.error(f"Error during data validation and transfer: {e}")
        prod_conn.rollback()
    finally:
        dev_cursor.close()
        prod_cursor.close()
        dev_conn.close()
        prod_conn.close()
