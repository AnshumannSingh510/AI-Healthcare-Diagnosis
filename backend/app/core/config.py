"""
Central application configuration, loaded from environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    PROJECT_NAME: str = "AI Healthcare Diagnosis Platform"
    API_V1_PREFIX: str = "/api/v1"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/healthcare_ai"

    # Redis / Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    # Auth
    JWT_SECRET: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Storage
    UPLOAD_DIR: str = "/app/storage/uploads"
    HEATMAP_DIR: str = "/app/storage/heatmaps"
    REPORT_DIR: str = "/app/storage/reports"

    # Model
    MODEL_WEIGHTS_PATH: str = "/app/model_weights/densenet121_chest.pt"
    MODEL_BACKBONE: str = "densenet121"
    MODEL_IMAGE_SIZE: int = 224

    # LLM (chatbot + explanation generation)
    LLM_PROVIDER: str = "none"  # "anthropic" | "openai" | "none" (template fallback)
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-6"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    DISCLAIMER: str = (
        "This is an AI-assisted prediction and not a confirmed medical diagnosis. "
        "Please consult a licensed physician for professional medical advice."
    )


settings = Settings()
