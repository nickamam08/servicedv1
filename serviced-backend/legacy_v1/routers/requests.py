from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models import RequestCreate
from dependencies import get_current_user
import mock_data
from datetime import datetime

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("/")
async def create_request(request: RequestCreate, current_user: dict = Depends(get_current_user)):
    new_request = {
        "request_id": mock_data.request_id_counter,
        "client_id": current_user['user_id'],
        "service_id": request.service_id,
        "status": "new",
        "initial_message": request.initial_message,
        "request_date": datetime.now()
    }
    
    mock_data.requests.append(new_request)
    mock_data.request_id_counter += 1
    
    return {"request_id": new_request['request_id'], "status": new_request['status']}

@router.get("/")
async def get_my_requests(current_user: dict = Depends(get_current_user)):
    results = []
    
    for r in mock_data.requests:
        service = next((s for s in mock_data.services if s['service_id'] == r['service_id']), None)
        if not service: continue
        
        # Filtrar basado en rol
        include = False
        if current_user['role'] == 'client' and r['client_id'] == current_user['user_id']:
            include = True
        elif current_user['role'] == 'provider' and service['provider_id'] == current_user['user_id']:
            include = True
        elif current_user['role'] == 'admin':
            include = True
            
        if include:
            r_copy = r.copy()
            r_copy['service_title'] = service['title']
            
            if current_user['role'] == 'client':
                 provider = next((u for u in mock_data.users if u['user_id'] == service['provider_id']), None)
                 r_copy['provider_name'] = provider['full_name'] if provider else "Desconocido"
            else:
                 client = next((u for u in mock_data.users if u['user_id'] == r['client_id']), None)
                 r_copy['client_name'] = client['full_name'] if client else "Desconocido"
            
            results.append(r_copy)
            
    return results
