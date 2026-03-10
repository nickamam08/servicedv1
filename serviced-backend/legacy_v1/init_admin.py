"""
Función para asegurar que el usuario admin siempre existe.
Se ejecuta al iniciar la aplicación.
"""
from utils import get_password_hash, verify_password
import mock_data

def ensure_admin_exists():
    """
    Asegura que el usuario admin siempre existe en la base de datos.
    Si no existe, lo crea. Si existe pero cambió la contraseña, la actualiza.
    """
    from database import get_db_connection, release_db_connection
    import psycopg2.extras
    
    admin_email = "admin@serviced.com"
    admin_password = "password123"
    
    # Intentar obtener conexión. Si falla (por ejemplo al iniciar), ignorar para no romper el arranque si la BD no está lista
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"⚠️ No se pudo conectar a la BD para verificar admin: {e}")
        return

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if admin exists
        cur.execute("SELECT * FROM users WHERE email = %s", (admin_email,))
        admin = cur.fetchone()
        
        if not admin:
            print("Creando usuario admin...")
            hashed_password = get_password_hash(admin_password)
            cur.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role, phone, location, avatar_initials)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                ("Super Admin", admin_email, hashed_password, "admin", "+123456789", "Nube", "SA")
            )
            conn.commit()
            print("Usuario admin creado exitosamente")
        else:
            # Verify password hash
            if not verify_password(admin_password, admin['password_hash']):
                print("Actualizando contraseña de admin...")
                new_hash = get_password_hash(admin_password)
                cur.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (new_hash, admin['user_id']))
                conn.commit()
                print("Contraseña de admin actualizada")
            else:
                print("Usuario admin verificado correctamente")
                
    except Exception as e:
        print(f"Error asegurando usuario admin: {e}")
    finally:
        if 'cur' in locals(): cur.close()
        release_db_connection(conn)

# Ejecutar al importar el módulo
if __name__ != "__main__":
    ensure_admin_exists()
