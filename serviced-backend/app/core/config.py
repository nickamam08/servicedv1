from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    """
    Configuración global de la aplicación cargada desde variables de entorno o valores por defecto.
    """
    PROJECT_NAME: str = "SERVICED API"
    API_V1_STR: str = "/api/v1"
    FRONTEND_HOST: str = "http://localhost:8000" # Host del frontend para redirecciones y CORS
    
    # Configuración de Base de Datos (PostgreSQL)
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "serviced_db"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # Seguridad y Autenticación
    SECRET_KEY: str = "supersecretkey123" # CLAVE SECRETA (Cambiar obligatoriamente en producción)
    ALGORITHM: str = "HS256" # Algoritmo de firma para los tokens JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # Duración del token (30 días por defecto)

    # Configuración de Correo Electrónico (SMTP)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True
    EMAILS_FROM_NAME: str = "SERVICED"
    EMAILS_FROM_EMAIL: str = "info@serviced.com"

    # Configuración de CORS (Intercambio de recursos entre orígenes)
    BACKEND_CORS_ORIGINS: List[str] = ["*"] # Permitir todo en desarrollo

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    def assemble_db_connection(self):
        """
        Construye la URL de conexión a la base de datos si no ha sido definida explícitamente.
        """
        if not self.SQLALCHEMY_DATABASE_URI:
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        return self.SQLALCHEMY_DATABASE_URI

# Instancia única de configuración para toda la app
settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = settings.assemble_db_connection()
