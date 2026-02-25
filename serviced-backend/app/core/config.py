from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "SERVICED API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "admin"
    POSTGRES_DB: str = "serviced_db"
    SQLALCHEMY_DATABASE_URI: str | None = None

    # Security
    SECRET_KEY: str = "supersecretkey123" # CHANGE THIS IN PRODUCTION
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days

    # SMTP (Emails)
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True
    EMAILS_FROM_NAME: str = "SERVICED"
    EMAILS_FROM_EMAIL: str = "info@serviced.com"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"] # Allow all for dev

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    def assemble_db_connection(self):
        if not self.SQLALCHEMY_DATABASE_URI:
            return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        return self.SQLALCHEMY_DATABASE_URI

settings = Settings()
settings.SQLALCHEMY_DATABASE_URI = settings.assemble_db_connection()

# Configuration loaded at startup
