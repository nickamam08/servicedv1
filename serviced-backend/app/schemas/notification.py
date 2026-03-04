from pydantic import BaseModel
from datetime import datetime

# Esquema para representar una notificación individual dirigida a un usuario
class NotificationResponse(BaseModel):
    id: int
    title: str # Título breve de la notificación
    message: str # Contenido descriptivo del aviso
    is_read: bool # Estado de lectura
    created_at: datetime

    class Config:
        from_attributes = True
