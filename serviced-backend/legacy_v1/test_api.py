import requests
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Probando API SERVICED...")
    
    # 1. Verificación de estado (Health Check)
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print("✅ La API está funcionando")
        else:
            print("❌ Falló la verificación de estado de la API")
            return
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API. ¿Está ejecutándose?")
        print("   Ejecuta: uvicorn main:app --reload")
        return

    # 2. Iniciar sesión (Usando datos de prueba)
    print("\n🔑 Probando Inicio de Sesión (Admin)...")
    login_data = {"email": "admin@serviced.com", "password": "password123"}
    r = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if r.status_code == 200:
        print("✅ Inicio de sesión exitoso")
        # El token lo usaremos del nuevo usuario más adelante
    else:
        print(f"❌ Falló el inicio de sesión: {r.text}")
    
    # Probemos registrar un NUEVO usuario.
    print("\n👤 Probando Registro...")
    new_user = {
        "full_name": "Usuario Prueba",
        "email": "prueba@ejemplo.com",
        "password": "password123",
        "phone": "1234567890",
        "location": "Ciudad Prueba",
        "role": "client"
    }
    
    # Verificar si el usuario existe (se espera fallo si se re-ejecuta)
    r = requests.post(f"{BASE_URL}/auth/register", json=new_user)
    token = None
    if r.status_code == 200:
        print("✅ Registro exitoso")
        token = r.json()['access_token']
    elif r.status_code == 400 and "registered" in r.text: # "registered" might still be in English in API response unless I change that too
        print("⚠️ El usuario ya existe, intentando iniciar sesión...")
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": new_user['email'], "password": new_user['password']})
        if r.status_code == 200:
            print("✅ Inicio de sesión exitoso")
            token = r.json()['access_token']
        else:
            print(f"❌ Falló el inicio de sesión: {r.text}")
            return
    else:
        print(f"❌ Falló el registro: {r.text}")
        return

    # 3. Obtener Servicios
    print("\n📦 Probando Obtener Servicios...")
    services = []
    r = requests.get(f"{BASE_URL}/services")
    if r.status_code == 200:
        services = r.json()
        print(f"✅ Se encontraron {len(services)} servicios")
    else:
        print(f"❌ Falló la obtención de servicios: {r.text}")

    # 4. Crear Solicitud
    if len(services) > 0 and token:
        print("\n📝 Probando Crear Solicitud...")
        service_id = services[0]['service_id']
        req_data = {"service_id": service_id, "initial_message": "Probando solicitud desde el script"}
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.post(f"{BASE_URL}/requests/", json=req_data, headers=headers)
        if r.status_code == 200:
            print("✅ Solicitud creada")
        else:
            print(f"❌ Falló la creación de la solicitud: {r.text}")

if __name__ == "__main__":
    test_api()
