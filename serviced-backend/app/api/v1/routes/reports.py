from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.deps import get_current_user
from app.models import User
from app.schemas.report import ReportCreate, ReportResponse
from app.services.report_service import report_service

router = APIRouter()

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo reporte (queja o incidencia). 
    Puede ser ejecutado por cualquier usuario autenticado.
    """
    return report_service.create_report(db, reporter_id=current_user.id, report_in=report_in)

@router.get("/my-reports", response_model=List[ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el listado de todos los reportes realizados por el usuario actual.
    """
    from app.models.all_models import Report
    return db.query(Report).filter(Report.reporter_id == current_user.id).all()
