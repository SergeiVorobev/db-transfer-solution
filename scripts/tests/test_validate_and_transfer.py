import unittest
import psycopg2
from dotenv import load_dotenv
import os

from validate_and_transfer import validate_and_transfer_data


load_dotenv()

class TestValidateAndTransfer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dev_conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_DEV_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        cls.prod_conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_PROD_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )

        cls.create_sample_data(cls.dev_conn)
        cls.create_sample_data(cls.prod_conn)

    @classmethod
    def tearDownClass(cls):
        cls.dev_conn.close()
        cls.prod_conn.close()

    @classmethod
    def create_sample_data(cls, conn):
        with conn.cursor() as cursor:
            # Clear existing data
            cursor.execute("DELETE FROM images;")
            cursor.execute("DELETE FROM documents;")
            cursor.execute("DELETE FROM companies;")
            cursor.execute("DELETE FROM categories;")

            # Insert sample data into categories
            cursor.execute("""
                INSERT INTO categories (id, title, description) 
                VALUES (1, 'Sample Category', 'Description of Sample Category');
            """)
            # Insert sample data into companies
            cursor.execute("""
                INSERT INTO companies (id, category_id, title, site_url, description) 
                VALUES (1, 1, 'Sample Company', 'http://example.com', 'Description of Sample Company');
            """)
            # Insert sample data into documents
            cursor.execute("""
                INSERT INTO documents (id, company_id, title, content) 
                VALUES (1, 1, 'Sample Document', 'Content of Sample Document');
            """)
            conn.commit()

    def test_validate_and_transfer(self):
        validate_and_transfer_data()

        with self.prod_conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE id = 1;")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Record with ID 1 was not found in PROD.")
            self.assertEqual(result[2], 'Sample Document')  # Checking title field

    def test_no_duplicate_records(self):
        validate_and_transfer_data()

        with self.prod_conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM documents WHERE id = 1;
            """)
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1, "Duplicate record with ID 1 found in PROD.")

if __name__ == '__main__':
    unittest.main()
