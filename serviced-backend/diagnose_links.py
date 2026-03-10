from app.db.session import SessionLocal
from app.models import Service, ProviderProfile, User

def diagnose():
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        print(f"Total services found: {len(services)}")
        for s in services:
            print(f"Service ID: {s.id}, Title: {s.title}")
            print(f"  - provider_id (FK): {s.provider_id}")
            provider = s.provider
            if provider:
                print(f"  - Provider Profile ID: {provider.id}")
                print(f"  - Provider User ID (property): {s.provider_user_id}")
                print(f"  - Actual User ID in Profile: {provider.user_id}")
            else:
                print("  - NO PROVIDER RELATIONSHIP FOUND!")
            print("-" * 20)
    finally:
        db.close()

if __name__ == "__main__":
    diagnose()
