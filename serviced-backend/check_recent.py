from app.db.session import SessionLocal
from app.models import User
from sqlalchemy import desc

def check_recent():
    db = SessionLocal()
    try:
        users = db.query(User).order_by(desc(User.created_at)).limit(10).all()
        print(f"{'ID':<5} | {'Email':<30} | {'Created At'}")
        print("-" * 60)
        for u in users:
            print(f"{u.id:<5} | {u.email:<30} | {u.created_at}")
    finally:
        db.close()

if __name__ == "__main__":
    check_recent()
