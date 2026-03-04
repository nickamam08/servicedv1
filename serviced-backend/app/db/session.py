from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Creación del motor de conexión a la base de datos (Engine)
# pool_pre_ping=True ayuda a reconectar automáticamente si la conexión se pierde
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, 
    pool_pre_ping=True,
    connect_args={"client_encoding": "utf8"}
)

# Fábrica de sesiones para interactuar con la base de datos de manera atómica
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Generador de sesiones de base de datos para usar como dependencia en las rutas de FastAPI.
    Asegura que la conexión se cierre correctamente después de cada solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
