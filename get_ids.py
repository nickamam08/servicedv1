
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "serviced-backend"))

from app.db.session import SessionLocal
from app.models.all_models import Service, ServiceRequest

def list_ids():
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        requests = db.query(ServiceRequest).all()
        
        with open('ids.txt', 'w', encoding='utf-8') as f:
            f.write("SERVICE IDs:\n")
            for s in services:
                # Use repr to avoid encoding issues when printing/writing
                f.write(f"{s.id}: {s.title}\n")
            
            f.write("\nREQUEST IDs:\n")
            for r in requests:
                f.write(f"{r.id}: {r.status}\n")
                
        print("IDs written to ids.txt")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_ids()
