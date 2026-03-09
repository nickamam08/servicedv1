
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configuración de hashing (mismo que usa el backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

try:
    engine = create_engine("postgresql+psycopg2://postgres:123456@127.0.0.1/serviced2.0")
    with engine.connect() as conn:
        # 1. Cambiar maciasalvareznicolas@gmail.com a provider
        result1 = conn.execute(text("UPDATE users SET role = 'provider' WHERE email = 'maciasalvareznicolas@gmail.com'"))
        print(f"maciasalvareznicolas@gmail.com updated to provider. Rows: {result1.rowcount}")
        
        # 2. Verificar o crear admin_master@serviced.com
        check_admin = conn.execute(text("SELECT id FROM users WHERE email = 'admin_master@serviced.com'")).first()
        
        if check_admin:
            result2 = conn.execute(text("UPDATE users SET role = 'admin', is_active = True WHERE email = 'admin_master@serviced.com'"))
            print(f"admin_master@serviced.com updated to admin. Rows: {result2.rowcount}")
        else:
            # Crear administrador maestro si no existe
            hashed_pwd = hash_password("Admin123!")
            conn.execute(text(
                "INSERT INTO users (full_name, email, password_hash, role, is_active, created_at) "
                "VALUES ('Admin Master', 'admin_master@serviced.com', :pwd, 'admin', True, NOW())"
            ), {"pwd": hashed_pwd})
            print("admin_master@serviced.com created as admin (Password: Admin123!)")
            
        conn.commit()
        print("Transaction committed successfully.")
except Exception as e:
    print(f"Error: {e}")
