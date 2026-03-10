from app.db.session import SessionLocal
from app.models import User

def list_all():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total: {len(users)}")
        for u in users:
            print(f"{u.id} | {u.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_all()
