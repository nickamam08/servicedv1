from fastapi import APIRouter, HTTPException, status, Depends
from models import UserLogin, UserRegister, Token
from utils import verify_password, get_password_hash, create_access_token
from database import get_db_connection, release_db_connection
import psycopg2.extras

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user: UserRegister):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if user exists
        cur.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
            
        hashed_password = get_password_hash(user.password)
        
        # Insert new user
        cur.execute(
            """
            INSERT INTO users (full_name, email, password_hash, role, phone, location, avatar_initials)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id, full_name, email, role, phone, location
            """,
            (
                user.full_name, 
                user.email, 
                hashed_password, 
                user.role, 
                user.phone, 
                user.location,
                "".join([n[0] for n in user.full_name.split()[:2]]).upper() # Generate initials
            )
        )
        new_user = cur.fetchone()
        conn.commit()
        
        # Create token
        access_token = create_access_token(data={"sub": new_user['email'], "role": new_user['role'], "user_id": new_user['user_id']})
        
        return {"access_token": access_token, "token_type": "bearer", "user": new_user}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        release_db_connection(conn)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cur.execute("SELECT * FROM users WHERE email = %s", (user_credentials.email,))
        user = cur.fetchone()
        
        if not user:
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
            
        if not verify_password(user_credentials.password, user['password_hash']):
            raise HTTPException(status_code=400, detail="Credenciales inválidas")
            
        # Create token
        access_token = create_access_token(data={"sub": user['email'], "role": user['role'], "user_id": user['user_id']})
        
        user_data = {
            "user_id": user['user_id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role'],
             "phone": user.get('phone'),
            "location": user.get('location'),
            "avatar_initials": user.get('avatar_initials')
        }
        
        return {"access_token": access_token, "token_type": "bearer", "user": user_data}
        
    except Exception as e:
        raise e
    finally:
        cur.close()
        release_db_connection(conn)
