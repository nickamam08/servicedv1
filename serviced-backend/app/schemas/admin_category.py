from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Estructura básica para las categorías de servicios gestionadas por el administrador
class CategoryBase(BaseModel):
    name: str # Nombre de la categoría (ej. "Limpieza", "Plomería")
    is_active: bool = True

# Esquema para la creación de una nueva categoría
class CategoryCreate(CategoryBase):
    pass

# Esquema para modificar el nombre o estado de una categoría existente
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

# Respuesta detallada de una categoría enviada al panel administrativo
class CategoryOut(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
