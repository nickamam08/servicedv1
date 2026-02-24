from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo

def get_platform_stats(db: Session):
    return admin_repo.fetch_platform_statistics(db)
