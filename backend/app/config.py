"""
NBK Salary API - Application Configuration

Uses pydantic-settings to load configuration from environment variables
and .env file. All settings can be overridden via environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # Database
    DATABASE_URL: str = "postgresql://nbk:nbk123@localhost:5432/nbk_salary"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # App
    APP_NAME: str = "NBK Salary API"
    DEBUG: bool = True

    # Salary calculation constants
    STANDARD_WORKING_DAYS: int = 26

    # Phụ cấp nghiệp vụ và kiêm nhiệm (VND) - Admin có thể thay đổi
    NGHIEP_VU_SUPPLEMENT: int = 2000000  # Mỗi nghiệp vụ +2M VND
    KIEM_NHIEM_SUPPLEMENT: int = 3000000  # Mỗi kiêm nhiệm +3M VND

    # Tax deductions (VND)
    PERSONAL_DEDUCTION: int = 11000000  # Giảm trừ bản thân 11M VND
    DEPENDENT_DEDUCTION: int = 4400000  # Giảm trừ người phụ thuộc 4.4M VND

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
