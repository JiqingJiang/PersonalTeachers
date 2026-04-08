"""应用配置 - 从环境变量加载"""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "PersonalTeachers"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/personal_teachers.db"

    # 管理员（首次启动时自动创建）
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""

    # SMTP（用于发送验证码）
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 路径
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    TEMPLATE_DIR: Path = BASE_DIR / "templates"
    STORAGE_DIR: Path = BASE_DIR / "storage"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
