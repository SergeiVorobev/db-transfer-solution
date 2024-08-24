CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    category_id INTEGER,
    site_url VARCHAR(255),
    title VARCHAR(255),
    description TEXT
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) UNIQUE,
    description TEXT
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    file_path VARCHAR(255) UNIQUE,
    title VARCHAR(255),
    description TEXT
);

CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    image_url VARCHAR(255) UNIQUE
);

CREATE TABLE companies_categories (
    company_id INTEGER REFERENCES companies(id),
    category_id INTEGER REFERENCES categories(id),
    PRIMARY KEY (company_id, category_id)
);
