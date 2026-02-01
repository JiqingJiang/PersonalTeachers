"""
数据模型定义

包含Pydantic模型（用于API）和SQLAlchemy模型（用于数据库）
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ============================================
# 枚举类型
# ============================================
class MentorCategory(str, Enum):
    """导师类别"""
    HISTORICAL = "historical"
    MODERN = "modern"
    COMMON = "common"
    FUTURE_SELF = "future_self"


class Perspective(str, Enum):
    """视角类型"""
    TOP = "top"
    BOTTOM = "bottom"
    EMOTIONAL = "emotional"
    RATIONAL = "rational"
    ULTIMATE = "ultimate"


# ============================================
# SQLAlchemy 数据库模型
# ============================================
class QuoteDB(Base):
    """语录表（数据库模型）"""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mentor_name = Column(String(100), nullable=False, index=True)
    mentor_category = Column(String(20), nullable=False, index=True)
    mentor_age = Column(Integer)
    keyword = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    ai_model = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    quality_score = Column(Float, default=0.0)  # 用户评分

    def __repr__(self):
        return f"<Quote {self.mentor_name} - {self.keyword}>"


class EmailLogDB(Base):
    """邮件发送日志表"""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    to_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Integer, nullable=False)  # 0失败 1成功
    error_message = Column(Text)
    quote_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<EmailLog {self.to_email} - {'✅' if self.success else '❌'}>"


# ============================================
# Pydantic 模型（用于API）
# ============================================
class Mentor(BaseModel):
    """导师数据模型"""
    id: str
    name: str
    category: MentorCategory
    age_range: tuple[int, int]
    field: str
    perspective: Perspective
    keywords: list[str]
    personality: str
    tone: str
    background: str
    era: Optional[str] = None
    achievements: Optional[list[str]] = None
    template_type: Optional[str] = None
    years_ahead: Optional[int] = None

    class Config:
        from_attributes = True


class Keyword(BaseModel):
    """关键词数据模型"""
    name: str
    english: str
    category: str
    default_weight: float
    description: str
    mentors_preferred: list[str]
    related_keywords: list[str]
    quadrant: int


class QuoteResponse(BaseModel):
    """语录响应模型"""
    id: int
    mentor_name: str
    mentor_category: str
    mentor_age: Optional[int]
    keyword: str
    content: str
    ai_model: str
    created_at: datetime
    quality_score: float = 0.0

    class Config:
        from_attributes = True


class QuoteCreate(BaseModel):
    """创建语录请求模型"""
    keyword: str
    mentor_id: str


class QuoteGenerateRequest(BaseModel):
    """批量生成语录请求"""
    count: int = Field(default=10, ge=1, le=20)
    keyword_weights: Optional[dict[str, float]] = None
    mentor_preferences: Optional[dict[str, float]] = None


class ConfigUpdate(BaseModel):
    """配置更新请求"""
    keyword_weights: Optional[dict[str, float]] = None
    delivery_time: Optional[str] = None
    delivery_enabled: Optional[bool] = None
    ai_model_primary: Optional[str] = None


class ConfigResponse(BaseModel):
    """配置响应模型"""
    user_name: str
    user_age: int
    user_profession: str
    user_email: str
    delivery_time: str
    delivery_enabled: bool
    keyword_weights: dict[str, float]
    mentor_preferences: dict[str, float]
    ai_model_primary: str


class StatsResponse(BaseModel):
    """统计信息响应"""
    total_quotes: int
    quotes_this_week: int
    quotes_this_month: int
    by_keyword: dict[str, int]
    by_mentor_category: dict[str, int]
    ai_model_usage: dict[str, int]
