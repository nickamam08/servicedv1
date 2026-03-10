from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Estructura base para los reportes o denuncias dentro de la plataforma
class ReportBase(BaseModel):
    title: str
    description: str # Explicación detallada del problema
    type: str # Categorías: behavior (comportamiento), payment (pago), content (contenido), technical (técnico)
    reported_user_id: Optional[int] = None # Usuario denunciado (opcional)
    service_id: Optional[int] = None # Servicio asociado al problema (opcional)
    request_id: Optional[int] = None # Solicitud específica asociada (opcional)

# Esquema para que un usuario cree un nuevo reporte
class ReportCreate(ReportBase):
    pass

# Esquema para que un administrador gestione y resuelva un reporte
class ReportUpdate(BaseModel):
    status: Optional[str] = None # Ej: "investigating", "resolved", "dismissed"
    priority: Optional[str] = None # Ej: "high", "medium", "low"
    admin_notes: Optional[str] = None # Notas internas para el equipo administrativo
    resolution: Optional[str] = None # Explicación de cómo se cerró el caso

# Respuesta detallada de un reporte con información de resolución
class ReportResponse(ReportBase):
    id: int
    reporter_id: int # ID del usuario que realizó la denuncia
    status: str
    priority: str
    admin_notes: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Datos enriquecidos para visualización en el panel administrativo
    reporter_name: Optional[str] = None
    reported_user_name: Optional[str] = None
    service_title: Optional[str] = None

    class Config:
        from_attributes = True
