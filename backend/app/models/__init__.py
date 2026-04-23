"""导入所有模型，确保 SQLAlchemy Base 注册所有表"""

from app.models.database import Base, init_db, get_session
from app.models.user import User
from app.models.keyword import Keyword, UserKeywordPref
from app.models.mentor import Mentor, UserMentorPref
from app.models.quote import Quote
from app.models.email_log import EmailSendLog
from app.models.email_pool import EmailPool
from app.models.ai_model import AIModel
from app.models.verification import VerificationCode

__all__ = [
    "Base",
    "init_db",
    "get_session",
    "User",
    "Keyword",
    "UserKeywordPref",
    "Mentor",
    "UserMentorPref",
    "Quote",
    "EmailSendLog",
    "EmailPool",
    "AIModel",
    "VerificationCode",
]
