from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.all_models import Report, User, Service
from app.schemas.report import ReportCreate, ReportUpdate
from app.repositories.report_repository import report_repo

class ReportService:
    def create_report(self, db: Session, reporter_id: int, report_in: ReportCreate) -> Report:
        db_obj = Report(
            reporter_id=reporter_id,
            reported_user_id=report_in.reported_user_id,
            service_id=report_in.service_id,
            request_id=report_in.request_id,
            title=report_in.title,
            description=report_in.description,
            type=report_in.type
        )
        return report_repo.create(db, obj_in=db_obj)

    def get_all_reports(self, db: Session, *, status: Optional[str] = None, priority: Optional[str] = None) -> List[dict]:
        reports = report_repo.fetch_all(db, status=status, priority=priority)
        enriched_reports = []
        for r in reports:
            # Enrichment
            reporter_name = r.reporter.full_name if r.reporter else "Desconocido"
            reported_user_name = r.reported_user.full_name if r.reported_user else "N/A"
            service_title = r.service.title if r.service else "N/A"
            
            enriched_reports.append({
                "id": r.id,
                "reporter_id": r.reporter_id,
                "reporter_name": reporter_name,
                "reported_user_id": r.reported_user_id,
                "reported_user_name": reported_user_name,
                "service_id": r.service_id,
                "service_title": service_title,
                "request_id": r.request_id,
                "title": r.title,
                "description": r.description,
                "type": r.type,
                "status": r.status,
                "priority": r.priority,
                "admin_notes": r.admin_notes,
                "resolution": r.resolution,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None
            })
        return enriched_reports

    def update_report(self, db: Session, report_id: int, report_in: ReportUpdate) -> Optional[Report]:
        db_obj = report_repo.get_by_id(db, report_id)
        if not db_obj:
            return None
        return report_repo.update(db, db_obj=db_obj, obj_in=report_in.dict(exclude_unset=True))

report_service = ReportService()
