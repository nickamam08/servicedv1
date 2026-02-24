from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.all_models import Category
from app.schemas.admin_category import CategoryCreate, CategoryUpdate

def get_all_categories(db: Session) -> List[Category]:
    return db.query(Category).all()

def create_category(db: Session, category_in: CategoryCreate) -> Category:
    db_obj = Category(
        name=category_in.name,
        is_active=category_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_category(db: Session, category_id: int, category_in: CategoryUpdate) -> Optional[Category]:
    db_obj = db.query(Category).filter(Category.id == category_id).first()
    if db_obj:
        update_data = category_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
    return db_obj

def delete_category(db: Session, category_id: int) -> bool:
    db_obj = db.query(Category).filter(Category.id == category_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False
