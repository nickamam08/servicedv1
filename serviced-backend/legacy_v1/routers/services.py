from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from models import ServiceResponse, ServiceCreate
from dependencies import get_current_user
import mock_data

router = APIRouter(prefix="/services", tags=["services"])

@router.get("/", response_model=List[ServiceResponse])
async def get_services(category: Optional[str] = None):
    results = []
    for s in mock_data.services:
        if s['is_active']:
            if category and s['category'] != category:
                continue
            
            # Enriquecer con nombre del proveedor
            provider = next((u for u in mock_data.users if u['user_id'] == s['provider_id']), None)
            s_copy = s.copy()
            s_copy['provider_name'] = provider['full_name'] if provider else "Desconocido"
            results.append(s_copy)
    return results

@router.post("/", response_model=ServiceResponse)
async def create_service(service: ServiceCreate, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'provider':
        raise HTTPException(status_code=403, detail="Solo los proveedores pueden crear servicios")
        
    new_service = {
        "service_id": mock_data.service_id_counter,
        "provider_id": current_user['user_id'],
        "title": service.title,
        "description": service.description,
        "category": service.category,
        "price": service.price,
        "price_unit": service.price_unit,
        "is_active": True,
        "provider_name": "Tú" # Marcador de posición
    }
    
    mock_data.services.append(new_service)
    mock_data.service_id_counter += 1
    
    return new_service
