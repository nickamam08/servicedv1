from app.db.session import SessionLocal
from app.models import User
from app.models.all_models import UserRole
from app.services import (
    admin_dashboard_service, admin_user_service, admin_category_service
)
from app.schemas.admin_category import CategoryCreate, CategoryUpdate

def test_admin_logic():
    db = SessionLocal()
    try:
        print("--- Testing Admin Overview Service ---")
        stats = admin_dashboard_service.get_platform_stats(db)
        print(f"Stats: {stats}")

        print("\n--- Testing List Users Service ---")
        users = admin_user_service.get_all_users(db)
        print(f"Found {len(users)} users.")

        print("\n--- Testing Category Flow Service ---")
        # Create category
        cat_in = CategoryCreate(name="Service Test Category", is_active=True)
        cat = admin_category_service.create_category(db, cat_in)
        print(f"Created Category: {cat.name} (ID: {cat.id})")
        
        # List categories
        cats = admin_category_service.get_all_categories(db)
        print(f"Found {len(cats)} categories.")
        
        # Update category
        cat_up = CategoryUpdate(name="Updated Service Test Category")
        updated_cat = admin_category_service.update_category(db, cat.id, cat_up)
        print(f"Updated Category: {updated_cat.name}")
        
        # Delete category
        success = admin_category_service.delete_category(db, cat.id)
        print(f"Delete Category Success: {success}")

    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_logic()
