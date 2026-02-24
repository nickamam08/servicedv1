import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def init_db():
    print("Inicializando Base de Datos...")
    
    try:
        conn = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME"),
            client_encoding='LATIN1'
        )
        cur = conn.cursor()
        
        # Helper function to read file with fallback encoding
        def read_sql_file(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(path, "r", encoding="latin-1") as f:
                    return f.read()

        # Update paths relative to this script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(base_dir, "../database/schema.sql")
        seed_path = os.path.join(base_dir, "../database/seed.sql")

        # Leer y ejecutar esquema
        print(f"Ejecutando {schema_path}...")
        cur.execute(read_sql_file(schema_path))
            
        # Leer y ejecutar datos de prueba (seed)
        print(f"Ejecutando {seed_path}...")
        cur.execute(read_sql_file(seed_path))
            
        conn.commit()
        cur.close()
        conn.close()
        print("Base de datos inicializada correctamente!")
        
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")
        if "password authentication failed" in str(e):
             print("Pista: Verifica DB_PASSWORD en el archivo .env")
        if 'database "' in str(e) and 'does not exist' in str(e):
             print("Pista: Necesitas crear la base de datos primero. Ejecuta: CREATE DATABASE serviced_db;")

if __name__ == "__main__":
    init_db()
