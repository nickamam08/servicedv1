from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.all_models import Report, ReportStatus

class ReportRepository:
    def create(self, db: Session, *, obj_in: Report) -> Report:
        db.add(obj_in)
        db.commit()
        db.refresh(obj_in)
        return obj_in

    def get_by_id(self, db: Session, id: int) -> Optional[Report]:
        return db.query(Report).filter(Report.id == id).first()

    def fetch_all(self, db: Session, *, status: Optional[str] = None, priority: Optional[str] = None) -> List[Report]:
        query = db.query(Report)
        if status:
            query = query.filter(Report.status == status)
        if priority:
            query = query.filter(Report.priority == priority)
        return query.order_by(Report.created_at.desc()).all()

    def update(self, db: Session, *, db_obj: Report, obj_in: dict) -> Report:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        db.commit()
        db.refresh(db_obj)
        return db_obj

report_repo = ReportRepository()
