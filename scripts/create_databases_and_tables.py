import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Connect to the PostgreSQL server
def connect_to_server(dbname):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=dbname,
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database '{dbname}': {e}")
        return None

# Creates a database
def create_database(conn, db_name):
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cursor:
        try:
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"Database '{db_name}' created successfully.")
        except Exception as e:
            print(f"Error creating database '{db_name}': {e}")

# Creates tables in the given database
def create_tables(conn):
    try:
        with conn.cursor() as cursor:
            # Create the categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT
                );
            """)

            # Create the companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                    site_url VARCHAR(255),
                    title VARCHAR(255) NOT NULL,
                    description TEXT
                );
            """)

            # Create the documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    title VARCHAR(255) NOT NULL,
                    content TEXT
                );
            """)

            # Create the images table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
                    image_url VARCHAR(255) NOT NULL,
                    description TEXT
                );
            """)

            # Create the joining table for companies and categories (many-to-many relationship)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies_categories (
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                    PRIMARY KEY (company_id, category_id)
                );
            """)

            # Example: Creating a unique index on the title of documents
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_title ON documents(title);")

            # Example: Creating a unique index on the URL of images
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_images_url ON images(image_url);")

            print("Tables created successfully.")
    except Exception as e:
        conn.rollback()  # Rollback transaction if error occurs
        print(f"Error creating tables: {e}")
    finally:
        conn.commit()

# Connect to the default database (e.g., postgres) to create "DEV" and "PROD" databases
default_conn = connect_to_server("postgres")
if default_conn:
    create_database(default_conn, os.getenv("DB_DEV_NAME"))
    create_database(default_conn, os.getenv("DB_PROD_NAME"))
    default_conn.close()

# Connect to the DEV database and create tables
dev_conn = connect_to_server(os.getenv("DB_DEV_NAME"))
if dev_conn:
    create_tables(dev_conn)
    dev_conn.close()

# Connect to the PROD database and create tables
prod_conn = connect_to_server(os.getenv("DB_PROD_NAME"))
if prod_conn:
    create_tables(prod_conn)
    prod_conn.close()
