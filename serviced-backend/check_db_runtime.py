from app.core.config import settings
from sqlalchemy import create_engine, inspect
import sys

def check_runtime():
    print(f"RUNTIME DATABASE URI: {settings.SQLALCHEMY_DATABASE_URI}")
    try:
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        insp = inspect(engine)
        tables = insp.get_table_names()
        print(f"TABLES FOUND: {tables}")
        
        for table in tables:
            cols = [c["name"] for c in insp.get_columns(table)]
            print(f"COLUMNS IN {table}: {cols}")
            
    except Exception as e:
        print(f"CONNECTION ERROR: {e}")

if __name__ == "__main__":
    check_runtime()
