from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# Middleware for logging
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Static frontend (para que puedas abrir todo desde el mismo puerto 8000)
BASE_DIR = Path(__file__).resolve().parent.parent  # app/..
PROJECT_ROOT = BASE_DIR.parent  # serviced-backend/..


users_frontend = PROJECT_ROOT / "serviced-users"
provider_frontend = PROJECT_ROOT / "serviced-provider"
admin_frontend = PROJECT_ROOT / "serviced-admin"

if users_frontend.is_dir():
    app.mount("/users", StaticFiles(directory=str(users_frontend), html=True), name="users")
if provider_frontend.is_dir():
    app.mount("/provider", StaticFiles(directory=str(provider_frontend), html=True), name="provider")
if admin_frontend.is_dir():
    app.mount("/admin", StaticFiles(directory=str(admin_frontend), html=True), name="admin")


@app.get("/")
def read_root():
    return {"message": "Welcome to SERVICED API V2 (SaaS Architecture)"}
