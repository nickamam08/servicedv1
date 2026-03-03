from app.db.session import SessionLocal
from app.models import Service

db = SessionLocal()
services = db.query(Service).all()
for s in services:
    if s.image_urls and len(s.image_urls) > 0:
        print(f"Service ID: {s.id}, Title: {s.title}, Image URLs: {s.image_urls}")
db.close()
