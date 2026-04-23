"""导师模型"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Mentor(Base):
    __tablename__ = "mentors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    age_range: Mapped[list | None] = mapped_column(JSON)
    field: Mapped[str | None] = mapped_column(String(100))
    perspective: Mapped[str | None] = mapped_column(String(20))
    keywords: Mapped[list | None] = mapped_column(JSON)
    personality: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(Text)
    background: Mapped[str | None] = mapped_column(Text)
    era: Mapped[str | None] = mapped_column(String(100))
    achievements: Mapped[list | None] = mapped_column(JSON)
    peak_age: Mapped[int | None] = mapped_column(Integer)
    peak_stage: Mapped[str | None] = mapped_column(String(100))
    peak_description: Mapped[str | None] = mapped_column(Text)
    years_ahead: Mapped[int | None] = mapped_column(Integer)
    representative_quotes: Mapped[list | None] = mapped_column(JSON)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class UserMentorPref(Base):
    __tablename__ = "user_mentor_prefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("user_id", "mentor_id", name="uq_user_mentor"),)
