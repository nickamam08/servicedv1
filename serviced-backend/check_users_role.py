from app.db.session import SessionLocal
from app.models.all_models import User

def check_users():
    db = SessionLocal()
    users = db.query(User).all()
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Role: '{u.role}', Type: {type(u.role)}")
    db.close()

if __name__ == "__main__":
    check_users()
