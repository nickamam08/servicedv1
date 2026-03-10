from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo

def get_platform_stats(db: Session):
    """
    Recupera las estadísticas globales de la plataforma (usuarios, servicios, solicitudes) para el dashboard administrativo.
    """
    return admin_repo.fetch_platform_statistics(db)
