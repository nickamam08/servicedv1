
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

CATEGORY_MAP = {
    "Technology": "Tecnología",
    "tech": "Tecnología",
    "Tech": "Tecnología",
    "Home": "Hogar",
    "home": "Hogar",
    "Design": "Diseño",
    "design": "Diseño",
    "Education": "Educación",
    "Wellness": "Bienestar",
    "Cleaning": "Limpieza",
    "Plumbing": "Plomería",
    "Electrical": "Electricidad",
    "Test": "Hogar" # Default test to Hogar
}

def main():
    # Login to get token (need provider/admin to update? actually only provider can update their own services normally)
    # But as a script, I can probably cheat if I have DB access, but through API I need to be the owner.
    # Uh oh. If I have multiple providers, I need to login as each or use a backdoor.
    
    # Check if there is a backdoor or admin endpoint.
    # There isn't one clearly visible.
    
    # Alternative: I'll use SQLAlchemy directly to update the DB, bypassing API auth for bulk fix.
    # This is safer and easier since I have local access.
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    from app.models import Service
    from app.core.config import settings
    
    # Need to setup sys.path to import app
    import os
    sys.path.append(os.getcwd())
    
    # Init DB
    # settings.SQLALCHEMY_DATABASE_URI might be loaded from env or default
    # Let's try to load it or guess it. Defaults usually sqlite.
    
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    
    try:
        services = db.query(Service).all()
        print(f"Found {len(services)} services.")
        
        updated_count = 0
        for s in services:
            original = s.category
            if original in CATEGORY_MAP:
                s.category = CATEGORY_MAP[original]
                print(f"Updating ID {s.id}: {original} -> {s.category}")
                updated_count += 1
            elif original not in ["Hogar", "Tecnología", "Diseño", "Educación", "Bienestar", "Limpieza", "Plomería", "Electricidad"]:
                # Default unknown to "Hogar" or leave it?
                # Let's leave it to avoid breaking things too much, or map to user choice.
                # For perol/tech, I added 'tech' to map.
                pass
                
        if updated_count > 0:
            db.commit()
            print(f"Successfully updated {updated_count} services.")
        else:
            print("No services needed updating.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
