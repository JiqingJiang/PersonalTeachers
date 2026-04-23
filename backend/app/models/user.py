"""用户模型"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer)
    profession: Mapped[str | None] = mapped_column(String(100))
    push_time: Mapped[str] = mapped_column(String(5), default="08:00", index=True)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    push_count: Mapped[int] = mapped_column(Integer, default=10)  # 每封邮件的语录数量，1~10
    max_words: Mapped[int] = mapped_column(Integer, default=100)  # 每条语录最大字数，<=200
    personal_bio: Mapped[str | None] = mapped_column(Text)  # 个人背景简介
    personalization_weight: Mapped[float] = mapped_column(Float, default=0.5)  # 个性化权重 0~1
    mentor_category_prefs: Mapped[dict | None] = mapped_column(
        JSON,
        default=lambda: {"historical": 0.3, "modern": 0.4, "common": 0.1, "future_self": 0.2},
    )
    last_push_date: Mapped[str | None] = mapped_column(String(10), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
