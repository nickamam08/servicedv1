from app.db.session import SessionLocal
from app.models import ChatConversation, User

def debug_chat_logic(user_id):
    db = SessionLocal()
    try:
        conversations = db.query(ChatConversation).filter(
            (ChatConversation.client_id == user_id) | (ChatConversation.provider_id == user_id)
        ).all()
        
        print(f"User ID: {user_id}")
        print(f"{'Conv ID':<8} | {'Client ID':<10} | {'Prov ID':<10} | {'Other User Name'}")
        print("-" * 60)
        
        for conv in conversations:
            # The logic from chat_service.py
            other_user = conv.provider if conv.client_id == user_id else conv.client
            
            # Print types for debugging
            # print(f"DEBUG: client_id: {type(conv.client_id)}, user_id: {type(user_id)}, match: {conv.client_id == user_id}")
            
            name = other_user.full_name if other_user else "N/A"
            print(f"{conv.id:<8} | {conv.client_id:<10} | {conv.provider_id:<10} | {name}")
            
    finally:
        db.close()

if __name__ == "__main__":
    # Test with a known user ID (e.g., 1 or 43 based on previous partial output)
    import sys
    uid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    debug_chat_logic(uid)
