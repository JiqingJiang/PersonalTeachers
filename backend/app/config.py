"""应用配置 - 环境分离支持"""

import os
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 环境：development | production
    APP_ENV: str = "development"

    # 应用
    APP_NAME: str = "PersonalTeachers"
    SECRET_KEY: str = "change-me-in-production"
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./storage/personal_teachers.db"

    # 管理员（首次启动时自动创建）
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""

    # SMTP
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

    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def _resolve_env_file() -> str:
    """根据 APP_ENV 决定加载哪个 .env 文件"""
    # 1. 环境变量显式指定
    env = os.getenv("APP_ENV", "")
    if env == "production":
        return ".env"
    if env == "development":
        return ".env.development"

    # 2. 本地存在 .env 文件 → 生产环境（服务器上直接用 .env）
    if Path(".env").exists():
        return ".env"

    # 3. 默认开发环境
    return ".env.development"


@lru_cache
def get_settings() -> Settings:
    env_file = _resolve_env_file()
    return Settings(_env_file=env_file)