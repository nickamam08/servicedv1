from fastapi import APIRouter
from app.api.v1.routes import (
    auth, users, services, requests, chat, dashboard, 
    providers, orders, provider_dashboard, admin_dashboard, reports, reviews
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(chat.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(provider_dashboard.router, prefix="/provider/dashboard", tags=["provider-dashboard"])
api_router.include_router(admin_dashboard.router, prefix="/admin/dashboard", tags=["admin-dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
