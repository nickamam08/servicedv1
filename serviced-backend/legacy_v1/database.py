import os
import psycopg2  
from psycopg2 import pool  
from dotenv import load_dotenv

load_dotenv()

connection_pool = None

try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # minconn (conexiones mínimas)
        20, # maxconn (conexiones máximas)
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        client_encoding='LATIN1'
    )
    if connection_pool:
        print("Pool de conexiones a la base de datos creado exitosamente")

except (Exception, psycopg2.DatabaseError) as error:
    print("Error conectando a PostgreSQL", error)

def get_db_connection():
    """Obtener una conexión del pool."""
    if connection_pool:
        return connection_pool.getconn()
    else:
        raise Exception("El pool de conexiones no está inicializado")

def release_db_connection(conn):
    """Devolver una conexión al pool."""
    if connection_pool and conn:
        connection_pool.putconn(conn)
