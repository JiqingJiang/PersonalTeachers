"""发件邮箱池模型"""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class EmailPool(Base):
    __tablename__ = "email_pool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    smtp_host: Mapped[str] = mapped_column(String(100), nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, default=587)
    smtp_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), default="PersonalTeachers")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_limit: Mapped[int] = mapped_column(Integer, default=200)
    sent_today: Mapped[int] = mapped_column(Integer, default=0)
    last_sent_date: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
