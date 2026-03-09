from app.db.session import SessionLocal
from app.models import User
from sqlalchemy import func

def check_collisions():
    db = SessionLocal()
    try:
        # Check if there are any emails that would collide if lowercased
        users = db.query(User).all()
        emails = [u.email.lower() for u in users]
        duplicates = [e for e in emails if emails.count(e) > 1]
        if duplicates:
            print(f"Found potential colliding emails (lowercased): {set(duplicates)}")
        else:
            print("No case-insensitive email collisions found in existing users.")
            
        # Try a case-insensitive search for a known email
        if users:
            first_email = users[0].email
            print(f"Searching for {first_email} case-insensitively...")
            res = db.query(User).filter(func.lower(User.email) == func.lower(first_email)).all()
            print(f"Found {len(res)} matches.")
    finally:
        db.close()

if __name__ == "__main__":
    check_collisions()
