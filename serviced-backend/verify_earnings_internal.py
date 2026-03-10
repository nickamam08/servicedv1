from app.db.session import SessionLocal
from app.repositories.provider_dashboard import ProviderDashboardRepository
from app.services.provider_dashboard_service import provider_dashboard_service
from app.models import User, ProviderProfile
import json

def test_earnings_logic():
    db = SessionLocal()
    try:
        # Buscamos un proveedor con perfil
        provider_profile = db.query(ProviderProfile).first()
        if not provider_profile:
            print("No se encontró ningún perfil de proveedor en la DB.")
            return
            
        repo = ProviderDashboardRepository(db)
        earnings = repo.get_total_earnings(provider_profile.id)
        print(f"Ganancias reales calculadas para el perfil {provider_profile.id}: ${earnings}")
        
        # Probamos el servicio
        user = db.query(User).filter(User.id == provider_profile.user_id).first()
        overview = provider_dashboard_service.get_dashboard_overview(db, user)
        
        print("\n--- DASHBOARD OVERVIEW RESULT ---")
        print(f"Balance en respuesta: ${overview.balance}")
        
        if overview.balance >= 150000.0:
            print("\nVERIFICACIÓN EXITOSA: El balance es >= 150.000 (Margen de ahorro aplicado o ganancias reales detectadas).")
        else:
            print("\nERROR: El balance sigue siendo menor al margen esperado.")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_earnings_logic()
