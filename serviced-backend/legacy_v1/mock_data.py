from utils import get_password_hash
from datetime import datetime, timedelta

# Almacén de Datos Simulados (Mock Data)

# Usuarios
# La contraseña para todos es 'password123'
users = [
    {
        "user_id": 1,
        "full_name": "Super Admin",
        "email": "admin@serviced.com",
        "password_hash": get_password_hash("password123"),
        "role": "admin",
        "phone": "+123456789",
        "location": "Nube"
    },
    {
        "user_id": 2,
        "full_name": "Ana María",
        "email": "ana@provider.com",
        "password_hash": get_password_hash("password123"),
        "role": "provider",
        "phone": "+34600111222",
        "location": "Madrid"
    },
    {
        "user_id": 3,
        "full_name": "Alejandro López",
        "email": "alex@client.com",
        "password_hash": get_password_hash("password123"),
        "role": "client",
        "phone": "+34600333444",
        "location": "Madrid"
    }
]

# Servicios
services = [
    {
        "service_id": 1,
        "provider_id": 2,
        "title": "Limpieza de Oficinas",
        "description": "Servicio profesional de limpieza...",
        "category": "home",
        "price": 45.0,
        "price_unit": "hour",
        "is_active": True,
        "created_at": datetime.now()
    }
]

# Solicitudes
requests = []

# Contadores de ID
user_id_counter = 4
service_id_counter = 2
request_id_counter = 1
