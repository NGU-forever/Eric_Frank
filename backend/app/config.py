"""
Application configuration using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Trade AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    START_MINIMAL: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./trade_ai.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/3"

    # AI Provider
    AI_PROVIDER: str = "tongyi"  # tongyi, qwen, openai
    TONGYI_API_KEY: str = ""
    TONGYI_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""

    # Email Service
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True

    # Gmail API
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:3000/callback/gmail"

    # Outlook API
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_REDIRECT_URI: str = "http://localhost:3000/callback/outlook"
    OUTLOOK_TENANT_ID: str = "common"

    # WhatsApp
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = ""

    # Data Service APIs
    APIFY_API_KEY: str = ""
    BRIGHT_DATA_API_KEY: str = ""
    ZYTE_API_KEY: str = ""

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = ""

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate Limiting
    EMAIL_RATE_LIMIT: int = 100  # emails per hour per account
    WHATSAPP_RATE_LIMIT: int = 60  # messages per hour

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    TEMPLATE_DIR: str = "./app/templates"
    CHROMA_DB_DIR: str = "./chroma_db"

    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
