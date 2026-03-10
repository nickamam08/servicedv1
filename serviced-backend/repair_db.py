from app.db.session import engine
from sqlalchemy import text
from app.db.base import Base
# Import everything to ensure metadata is populated
from app.models.all_models import Category, User, ProviderProfile, Service, ServiceRequest, Review, ChatConversation, ChatMessage, Report, Notification, Order

def repair_db():
    print("Repairing database schema...")
    
    # 1. Ensure all tables from models exist
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Add missing columns that create_all misses for existing tables
    queries = [
        # Services
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;",
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS image_urls JSONB;",
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS faqs JSONB;",
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS rating FLOAT DEFAULT 0.0;",
        "ALTER TABLE services ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;",
        
        # Provider Profiles
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS specialty VARCHAR;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS skills VARCHAR;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS social_links JSONB;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS latitude FLOAT;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS longitude FLOAT;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS certifications JSONB;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS languages VARCHAR;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS base_rate FLOAT DEFAULT 0.0;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS location VARCHAR;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS availability VARCHAR;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE provider_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;",
        
        # Users
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_initials VARCHAR;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;",
        
        # Reviews
        "ALTER TABLE reviews ADD COLUMN IF NOT EXISTS service_request_id INTEGER REFERENCES service_requests(id);",
        
        # Orders
        "ALTER TABLE orders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();",
        
        # Notifications
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS type VARCHAR;",
        
        # Reports
        "ALTER TABLE reports ADD COLUMN IF NOT EXISTS request_id INTEGER REFERENCES service_requests(id);",
        "ALTER TABLE reports ADD COLUMN IF NOT EXISTS admin_notes VARCHAR;",
        "ALTER TABLE reports ADD COLUMN IF NOT EXISTS resolution VARCHAR;",
        "ALTER TABLE reports ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;",
        
        # Drop legacy tables
        "DROP TABLE IF EXISTS messages CASCADE;"
    ]
    
    with engine.connect() as con:
        for q in queries:
            try:
                con.execute(text(q))
                con.commit()
                print(f"Executed: {q}")
            except Exception as e:
                print(f"Error executing {q}: {e}")
                con.rollback()
    
    print("Database repair complete.")

if __name__ == "__main__":
    repair_db()
