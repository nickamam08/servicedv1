from sqlalchemy.orm import Session
from app.models import User
from app.repositories.provider_dashboard import ProviderDashboardRepository
from app.schemas.provider_dashboard import DashboardOverview, UpcomingJob

class ProviderDashboardService:
    def get_dashboard_overview(self, db: Session, current_user: User) -> DashboardOverview:
        repo = ProviderDashboardRepository(db)
        provider_profile = repo.get_provider_profile(current_user.id)
        
        if not provider_profile:
             # If no profile, return zeros
             return DashboardOverview(
                 total_services=0, active_services=0, total_requests=0,
                 pending_requests=0, accepted_requests=0, completed_requests=0,
                 cancelled_requests=0, average_rating=0.0, total_reviews=0,
                 unread_messages=0, balance=0.0, upcoming_jobs=[]
             )

        service_stats = repo.get_service_stats(provider_profile.id)
        request_stats = repo.get_request_stats(provider_profile.id)
        upcoming = repo.get_upcoming_jobs(provider_profile.id)
        unread = repo.get_unread_messages_count(current_user.id)
        
        # Calculate balance (Mocked for now as per instructions "NO incluir sistema de pagos")
        # In a real system, this would sum up completed service requests prices
        balance = 0.0 
        
        upcoming_jobs_response = []
        for req in upcoming:
            # Safely get title
            svc_title = req.service.title if req.service else "Servicio eliminado"
            client_name = req.client.full_name if req.client else "Cliente desconocido"
            upcoming_jobs_response.append(UpcomingJob(
                id=req.id,
                client_name=client_name,
                service_title=svc_title,
                scheduled_date=req.scheduled_date,
                status=req.status
            ))

        return DashboardOverview(
            total_services=service_stats["total"],
            active_services=service_stats["active"],
            total_requests=request_stats["total"],
            pending_requests=request_stats["pending"],
            accepted_requests=request_stats["accepted"], # Mapping from ACTIVE
            completed_requests=request_stats["completed"],
            cancelled_requests=request_stats["cancelled"],
            average_rating=provider_profile.rating_average,
            total_reviews=provider_profile.total_reviews,
            unread_messages=unread,
            balance=balance,
            upcoming_jobs=upcoming_jobs_response
        )

provider_dashboard_service = ProviderDashboardService()
