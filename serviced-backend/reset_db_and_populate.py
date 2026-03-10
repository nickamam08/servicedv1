from sqlalchemy.orm import Session, configure_mappers
from app.db.base import Base
from app.models.all_models import User, ChatConversation, ChatMessage, ProviderProfile, Service, ServiceRequest
from app.db.session import engine, SessionLocal
from app.core.security import get_password_hash

def reset_and_populate():
    try:
        print("Configuring mappers...")
        configure_mappers()
        print("Mappers configured.")
        
        print("Resetting database...")
        # Force completion of drop/create
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        engine.dispose() # Ensure connections are clean
        print("Database reset complete.")
    except Exception as e:
        print(f"FAIL DDL: {e}")
        import traceback
        traceback.print_exc()
        return

    db = SessionLocal()
    try:
        print("Creating users...")
        p_user = User(
            full_name="Juan Provider V2",
            email="provider_v2@example.com",
            password_hash=get_password_hash("password123"),
            role="provider",
            is_active=True,
            avatar_initials="JP"
        )
        db.add(p_user)
        
        c_user = User(
            full_name="Maria Cliente V2",
            email="client_v2@example.com",
            password_hash=get_password_hash("password123"),
            role="client",
            is_active=True,
            avatar_initials="MC"
        )
        db.add(c_user)
        db.commit()
        db.refresh(p_user)
        db.refresh(c_user)

        print("Creating provider profile...")
        profile = ProviderProfile(
            user_id=p_user.id,
            description="Experto en reparaciones",
            experience_years=5
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        print("Creating service...")
        service = Service(
            provider_id=profile.id,
            title="Limpieza Profunda",
            price=80.0,
            is_active=True
        )
        db.add(service)
        db.commit()
        db.refresh(service)

        print("Creating conversation...")
        conv = ChatConversation(
            client_id=c_user.id,
            provider_id=p_user.id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

        print("Creating message...")
        msg = ChatMessage(
            conversation_id=conv.id,
            sender_id=c_user.id,
            content="Hola! ¿Vienes mañana?"
        )
        db.add(msg)
        db.commit()

        print("Population complete!")

    except Exception as e:
        print(f"Population error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_populate()
