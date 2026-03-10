from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.all_models import Report, ReportStatus

class ReportRepository:
    """
    Repositorio para gestionar reportes, quejas y denuncias de usuarios.
    """
    def create(self, db: Session, *, obj_in: Report) -> Report:
        """
        Guarda un nuevo reporte en la base de datos.
        """
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def get_by_id(self, db: Session, id: int) -> Optional[Report]:
        """
        Obtiene un reporte específico por su ID.
        """
        return db.query(Report).filter(Report.id == id).first()

    def fetch_all(self, db: Session, *, status: Optional[str] = None, priority: Optional[str] = None) -> List[Report]:
        """
        Obtiene la lista de reportes con filtros por estado y prioridad.
        Los resultados se ordenan del más reciente al más antiguo.
        """
        query = db.query(Report)
        if status:
            query = query.filter(Report.status == status)
        if priority:
            query = query.filter(Report.priority == priority)
        return query.order_by(Report.created_at.desc()).all()

    def update(self, db: Session, *, db_obj: Report, obj_in: dict) -> Report:
        """
        Actualiza los campos de un reporte existente (ej. cambiar estado o añadir notas de admin).
        """
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

# Instancia global del repositorio de reportes
report_repo = ReportRepository()
