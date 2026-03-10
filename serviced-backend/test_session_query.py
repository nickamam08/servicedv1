from app.db.session import SessionLocal
from app.models import Service, ProviderProfile
from sqlalchemy.orm import joinedload
import sys

def test_query():
    db = SessionLocal()
    try:
        print("Running test query...")
        # Exact same query as in services.py
        query = db.query(Service).options(joinedload(Service.provider)).join(Service.provider).filter(Service.is_active == True)
        results = query.all()
        print(f"Success! Found {len(results)} services.")
        for s in results:
            print(f"Service: {s.title}")
            if s.provider:
                print(f"  Provider Specialty: {s.provider.specialty}")
                print(f"  Provider Full Name: {s.provider.full_name}")
                print(f"  Total Reviews: {s.provider.total_reviews}")
                print(f"  Rating Avg: {s.provider.rating_average}")
    except Exception as e:
        print(f"QUERY FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()
