
import sys
import os
import traceback

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "serviced-backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.all_models import Service, ServiceRequest

def list_ids_sqlite():
    # Force SQLite for local testing if Postgres fails
    db_path = os.path.abspath(os.path.join(os.getcwd(), "serviced-backend", "serviced.db"))
    db_url = f"sqlite:///{db_path}"
    print(f"Connecting to: {db_url}")
    
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        services = db.query(Service).all()
        requests = db.query(ServiceRequest).all()
        
        with open('ids_safe.txt', 'wb') as f:
            f.write(b"SERVICE IDs:\n")
            for s in services:
                line = f"{s.id}: {s.title}\n".encode('utf-8', errors='replace')
                f.write(line)
            
            f.write(b"\nREQUEST IDs:\n")
            for r in requests:
                line = f"{r.id}: {r.status}\n".encode('utf-8', errors='replace')
                f.write(line)
        
        print("Successfully wrote to ids_safe.txt")
                
    except Exception as e:
        with open('ids_error.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))
            f.write("\n")
            f.write(traceback.format_exc())
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_ids_sqlite()
