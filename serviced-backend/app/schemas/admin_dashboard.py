from typing import Optional
from pydantic import BaseModel

# Esquema consolidado para las estadísticas globales mostradas en el dashboard del administrador
class PlatformStats(BaseModel):
    total_users: int # Total de usuarios registrados (clientes + proveedores)
    total_providers: int # Proveedores totales
    total_services: int # Servicios publicados totales
    total_requests: int # Cantidad histórica de solicitudes
    total_completed_requests: int
    total_cancelled_requests: int
    total_reviews: int
    average_platform_rating: float # Calificación promedio general del sitio
    new_users_last_30_days: int
    new_requests_last_30_days: int

    class Config:
        from_attributes = True
