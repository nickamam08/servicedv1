from app.db.session import SessionLocal
from app.models import ChatConversation, User

def debug_full():
    db = SessionLocal()
    try:
        convs = db.query(ChatConversation).all()
        print(f"{'CID':<5} | {'CL_ID':<5} | {'PR_ID':<5} | {'CL_Name':<15} | {'PR_Name':<15}")
        print("-" * 60)
        for c in convs:
            cl_name = c.client.full_name if c.client else "N/A"
            pr_name = c.provider.full_name if c.provider else "N/A"
            print(f"{c.id:<5} | {c.client_id:<5} | {c.provider_id:<5} | {cl_name:<15} | {pr_name:<15}")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_full()
