from app.db.session import SessionLocal
from app.models import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"{'ID':<5} | {'Role':<10} | {'Full Name':<20} | {'Email'}")
        print("-" * 60)
        for u in users:
            print(f"{u.id:<5} | {u.role:<10} | {u.full_name:<20} | {u.email}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
