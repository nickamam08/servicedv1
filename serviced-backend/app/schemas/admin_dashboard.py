from typing import Optional
from pydantic import BaseModel

class PlatformStats(BaseModel):
    total_users: int
    total_providers: int
    total_services: int
    total_requests: int
    total_completed_requests: int
    total_cancelled_requests: int
    total_reviews: int
    average_platform_rating: float
    new_users_last_30_days: int
    new_requests_last_30_days: int

    class Config:
        from_attributes = True
