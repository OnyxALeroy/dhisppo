from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_PASSWORD: Optional[str] = None
    ORGANIZER_PASSWORD: Optional[str] = None
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    FRONTEND_URL: str = "http://localhost:3000"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Dhisppo"

    class Config:
        env_file = ".env"

    @property
    def database_url_masked(self) -> str:
        if not self.DATABASE_URL:
            return "Not configured"
        if "@" in self.DATABASE_URL:
            return self.DATABASE_URL.split("@")[0] + "@***"
        return self.DATABASE_URL


settings = Settings()
