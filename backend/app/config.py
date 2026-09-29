from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "SmartCook"
    DEBUG: bool = True
    SECRET_KEY: str = "smartcook_super_secret_jwt_key_2026_material_u"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/smartcook"

    # API & OAuth Keys
    GEMINI_API_KEY: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None

    # SMTP Mailer Settings for real OTP sending
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
