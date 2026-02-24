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
    Create a new report. Can be called by any authenticated user.
    """
    return report_service.create_report(db, reporter_id=current_user.id, report_in=report_in)

@router.get("/my-reports", response_model=List[ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reports made by the current user.
    """
    # We could add a fetch_by_reporter in repo, but for now we filter here or add it
    from app.models.all_models import Report
    return db.query(Report).filter(Report.reporter_id == current_user.id).all()
