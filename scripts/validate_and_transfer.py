import psycopg2
import os
from dotenv import load_dotenv
from extract_data_from_dev import extract_new_records

load_dotenv()

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
        # Extract data from the DEV database
        documents_data = extract_new_records()

        # Iterate over the documents data
        for document in documents_data:
            document_id = document[0]
            company_id = document[1]
            title = document[2]
            content = document[3]

            # Insert or update the document in the PROD database
            prod_cursor.execute("""
                INSERT INTO documents (id, company_id, title, content)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET company_id = EXCLUDED.company_id,
                              title = EXCLUDED.title,
                              content = EXCLUDED.content;
            """, (document_id, company_id, title, content))

        # Commit the transaction
        prod_conn.commit()

    except Exception as e:
        print(f"Error during data validation and transfer: {e}")
        prod_conn.rollback()
    finally:
        dev_cursor.close()
        prod_cursor.close()
        dev_conn.close()
        prod_conn.close()
