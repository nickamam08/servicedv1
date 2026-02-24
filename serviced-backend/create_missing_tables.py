
from app.db.session import engine
from app.db.base import Base
from app.models.all_models import Category, User, ProviderProfile, Service, ServiceRequest, Review, ChatConversation, ChatMessage, Report, Notification, Order

def init_db():
    print("Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
