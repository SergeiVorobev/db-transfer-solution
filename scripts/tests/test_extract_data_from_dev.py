import unittest
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

class TestDatabaseOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_DEV_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        cls.create_sample_data()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    @classmethod
    def create_sample_data(cls):
        with cls.conn.cursor() as cursor:
            # Clear existing data
            cursor.execute("DELETE FROM images;")
            cursor.execute("DELETE FROM documents;")
            cursor.execute("DELETE FROM companies_categories;")
            cursor.execute("DELETE FROM companies;")
            cursor.execute("DELETE FROM categories;")

            # Insert sample data into categories
            cursor.execute("""
                INSERT INTO categories (title, description) 
                VALUES ('Sample Category', 'Description of Sample Category');
            """)
            cursor.execute("SELECT id FROM categories WHERE title = 'Sample Category';")
            category_id = cursor.fetchone()[0]

            # Insert sample data into companies
            cursor.execute("""
                INSERT INTO companies (category_id, title, site_url, description) 
                VALUES (%s, 'Sample Company', 'http://example.com', 'Description of Sample Company');
            """, (category_id,))
            cursor.execute("SELECT id FROM companies WHERE title = 'Sample Company';")
            company_id = cursor.fetchone()[0]

            # Insert sample data into documents
            cursor.execute("""
                INSERT INTO documents (company_id, title, content) 
                VALUES (%s, 'Sample Document', 'Content of Sample Document');
            """, (company_id,))
            cursor.execute("SELECT id FROM documents WHERE title = 'Sample Document';")
            document_id = cursor.fetchone()[0]

            # Insert sample data into images
            cursor.execute("""
                INSERT INTO images (document_id, image_url, description) 
                VALUES (%s, 'http://example.com/image.jpg', 'Sample Image Description');
            """, (document_id,))

            # Insert sample data into companies_categories (many-to-many relationship)
            cursor.execute("""
                INSERT INTO companies_categories (company_id, category_id) 
                VALUES (%s, %s);
            """, (company_id, category_id))

            cls.conn.commit()

    def test_categories_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM categories WHERE title = 'Sample Category';")
            category = cursor.fetchone()
            self.assertIsNotNone(category)
            self.assertEqual(category[1], 'Sample Category')  # Index 1 for 'title'

    def test_companies_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM companies WHERE title = 'Sample Company';")
            company = cursor.fetchone()
            self.assertIsNotNone(company)
            self.assertEqual(company[3], 'Sample Company')  # Index 3 for 'title'

    def test_documents_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE title = 'Sample Document';")
            document = cursor.fetchone()
            self.assertIsNotNone(document)
            self.assertEqual(document[2], 'Sample Document')  # Index 2 for 'title'

    def test_images_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM images WHERE image_url = 'http://example.com/image.jpg';")
            image = cursor.fetchone()
            self.assertIsNotNone(image)
            self.assertEqual(image[2], 'http://example.com/image.jpg')  # Index 2 for 'image_url'

    def test_companies_categories_relationship(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM companies_categories 
                WHERE company_id = (SELECT id FROM companies WHERE title = 'Sample Company')
                AND category_id = (SELECT id FROM categories WHERE title = 'Sample Category');
            """)
            relation = cursor.fetchone()
            self.assertIsNotNone(relation)
            self.assertEqual(relation[0], self.get_company_id())  # Company ID
            self.assertEqual(relation[1], self.get_category_id())  # Category ID

    def get_company_id(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM companies WHERE title = 'Sample Company';")
            return cursor.fetchone()[0]

    def get_category_id(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id FROM categories WHERE title = 'Sample Category';")
            return cursor.fetchone()[0]

if __name__ == '__main__':
    unittest.main()
