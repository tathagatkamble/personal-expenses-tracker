import os
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL from .env or environment
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL and os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                DATABASE_URL = line.strip().split("=", 1)[1]
                break

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment or .env file.")

# Clean up channel_binding query param if present for compatibility with standard psycopg2
if "channel_binding=" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("&channel_binding=require", "").replace("?channel_binding=require", "?").rstrip("?")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    expense_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(category_id),
    amount NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    payment_method VARCHAR(50),
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS income (
    income_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    income_date DATE NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS budgets (
    budget_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(category_id),
    amount NUMERIC(12, 2) NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL
);

-- Seed standard categories if empty
INSERT INTO categories (category_name)
VALUES 
    ('Housing & Rent'),
    ('Food & Dining'),
    ('Utilities & Bills'),
    ('Transportation'),
    ('Entertainment'),
    ('Healthcare'),
    ('Shopping & Misc'),
    ('Education'),
    ('Other')
ON CONFLICT (category_name) DO NOTHING;
"""

def init_db():
    print("Connecting to Neon PostgreSQL cloud database...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(SCHEMA_SQL)
        print("Tables created and seeded successfully!")
        
        # Verify tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print("Verified tables in Neon database:")
        for t in tables:
            print(f"- {t[0]}")
    conn.close()

if __name__ == "__main__":
    init_db()
