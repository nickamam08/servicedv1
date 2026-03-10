import sys
import os
from sqlalchemy import text
from app.db.session import engine

def create_categories_table():
    print("--- CREATING CATEGORIES TABLE ---")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Creating categories table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR NOT NULL UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            trans.commit()
            print("Categories table created successfully.")
        except Exception as e:
            trans.rollback()
            print(f"Failed to create categories table: {e}")

if __name__ == "__main__":
    # Ensure sys.path is correct if running from backend root
    sys.path.append(os.getcwd())
    create_categories_table()
