from fastapi import APIRouter, HTTPException, status, Depends
from models import UserResponse, UserUpdate
from database import get_db_connection, release_db_connection
from dependencies import get_current_user
import psycopg2.extras

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("SELECT * FROM users WHERE user_id = %s", (current_user['user_id'],))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return user
        
    except Exception as e:
        raise e
    finally:
        cur.close()
        release_db_connection(conn)

@router.put("/me", response_model=UserResponse)
async def update_user_me(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Build query dynamically
        update_fields = []
        values = []
        
        if user_update.full_name is not None:
            update_fields.append("full_name = %s")
            values.append(user_update.full_name)
            # Update initials
            initials = "".join([n[0] for n in user_update.full_name.split()[:2]]).upper()
            update_fields.append("avatar_initials = %s")
            values.append(initials)
            
        if user_update.phone is not None:
            update_fields.append("phone = %s")
            values.append(user_update.phone)
            
        if user_update.location is not None:
            update_fields.append("location = %s")
            values.append(user_update.location)
            
        if not update_fields:
            # No changes, return current user
            cur.execute("SELECT * FROM users WHERE user_id = %s", (current_user['user_id'],))
            return cur.fetchone()
            
        values.append(current_user['user_id'])
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s RETURNING *"
        
        cur.execute(query, tuple(values))
        updated_user = cur.fetchone()
        conn.commit()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        release_db_connection(conn)
