
from app.db.session import SessionLocal
from app.models.all_models import Category

def add_test_category():
    db = SessionLocal()
    try:
        if not db.query(Category).filter(Category.name == "Prueba").first():
            cat = Category(name="Prueba", is_active=True)
            db.add(cat)
            db.commit()
            print("Added test category 'Prueba'")
        else:
            print("Test category 'Prueba' already exists.")
    except Exception as e:
        print(f"Error adding test category: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_test_category()
