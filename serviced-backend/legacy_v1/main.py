from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, services, requests, users
import init_admin  # Asegura que el admin siempre existe

app = FastAPI(title="API SERVICED", version="1.0.0")

# Asegurar que el admin existe al iniciar la aplicación
init_admin.ensure_admin_exists()

# Configuración de CORS (Intercambio de recursos de origen cruzado)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500", # Por defecto en Live Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permitir todos para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(services.router)
app.include_router(requests.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de SERVICED"}
