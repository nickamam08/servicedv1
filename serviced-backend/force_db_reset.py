from app.db.session import engine, SessionLocal
from sqlalchemy import text
from app.db.base import Base
from app.models.all_models import Category, User, ProviderProfile, Service, ServiceRequest, Review, ChatConversation, ChatMessage, Report, Notification, Order
from app.core.security import get_password_hash

def force_reset():
    print("Force resetting database schema...")
    with engine.connect() as con:
        try:
            # Drop schema cascade is Postgres specific and very thorough
            con.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres; GRANT ALL ON SCHEMA public TO public;"))
            con.commit()
            print("Schema public dropped and recreated.")
        except Exception as e:
            print(f"Error dropping schema: {e}")
            con.rollback()
    
    print("Creating all tables from models...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    print("Creating admin user...")
    db = SessionLocal()
    try:
        admin = User(
            full_name="Admin Principal",
            email="admin@serviced.com",
            password_hash=get_password_hash("AdminPassword2026!"),
            role="admin",
            is_active=True,
            avatar_initials="AP"
        )
        db.add(admin)
        db.commit()
        print("Admin user created.")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    force_reset()
