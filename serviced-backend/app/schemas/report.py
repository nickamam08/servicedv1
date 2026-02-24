from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ReportBase(BaseModel):
    title: str
    description: str
    type: str # behavior, payment, content, technical
    reported_user_id: Optional[int] = None
    service_id: Optional[int] = None
    request_id: Optional[int] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    admin_notes: Optional[str] = None
    resolution: Optional[str] = None

class ReportResponse(ReportBase):
    id: int
    reporter_id: int
    status: str
    priority: str
    admin_notes: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Enrichment
    reporter_name: Optional[str] = None
    reported_user_name: Optional[str] = None
    service_title: Optional[str] = None

    class Config:
        from_attributes = True
