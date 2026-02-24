
from app.db.session import SessionLocal
from app.models.all_models import Category

def check_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        print(f"Total categories found: {len(categories)}")
        for cat in categories:
            print(f"ID: {cat.id}, Name: {cat.name}, Active: {cat.is_active}")
    except Exception as e:
        print(f"Error checking categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_categories()
