from app.db.session import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).filter(User.avatar_url != None).all()
for u in users:
    print(f"User ID: {u.id}, Name: {u.full_name}, Avatar URL: {u.avatar_url}")
db.close()
