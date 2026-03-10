import sys
import os
from sqlalchemy import text
from app.db.session import engine

def migrate_schema():
    print("--- MIGRATING SCHEMA ---")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            print("Adding columns to provider_profiles...")
            conn.execute(text("ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS location VARCHAR;"))
            conn.execute(text("ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS availability VARCHAR;"))
            conn.execute(text("ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;")) # Added this to model too
            
            print("Adding columns to services...")
            conn.execute(text("ALTER TABLE services ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;"))
            conn.execute(text("ALTER TABLE services ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;"))

            print("Adding columns to notifications...")
            conn.execute(text("ALTER TABLE notifications ADD COLUMN IF NOT EXISTS type VARCHAR;"))
            
            print("Adding columns to reviews (if missing)...")
            conn.execute(text("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS service_request_id INTEGER REFERENCES service_requests(id);"))

            trans.commit()
            print("Migration successful.")
        except Exception as e:
            trans.rollback()
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    # Ensure sys.path is correct if running from backend root
    sys.path.append(os.getcwd())
    migrate_schema()
