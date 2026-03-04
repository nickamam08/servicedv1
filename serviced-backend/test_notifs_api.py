from app.db.session import SessionLocal
from app.models import Notification, User, UserRole
import json

def test_api_logic():
    db = SessionLocal()
    try:
        # Buscamos un proveedor
        provider = db.query(User).filter(User.role == UserRole.PROVIDER).first()
        if not provider:
            print("No se encontró ningún proveedor.")
            return
            
        user_id = provider.id
        print(f"Probando para usuario ID: {user_id}")
        
        # Simulamos lo que hace el repositorio
        notifs = db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).all()
        
        print(f"Resultado (registros): {len(notifs)}")
        for n in notifs[:5]:
            print(f"- {n.title} ({n.created_at})")

    finally:
        db.close()

if __name__ == "__main__":
    test_api_logic()
