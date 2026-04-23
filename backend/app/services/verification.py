"""验证码服务"""

import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verification import VerificationCode


class VerificationService:
    """验证码生成、发送、校验"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_code(self, email: str, purpose: str) -> str:
        """生成6位验证码，保存到数据库，返回验证码"""
        code = f"{random.randint(0, 999999):06d}"
        verification = VerificationCode(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(verification)
        await self.db.commit()
        return code

    async def validate_code(self, email: str, code: str, purpose: str) -> bool:
        """验证码校验"""
        result = await self.db.execute(
            select(VerificationCode).where(
                and_(
                    VerificationCode.email == email,
                    VerificationCode.code == code,
                    VerificationCode.purpose == purpose,
                    VerificationCode.is_used == False,
                )
            ).order_by(VerificationCode.created_at.desc())
        )
        verification = result.scalar_one_or_none()

        if verification is None:
            return False
        if verification.is_expired():
            return False

        # 标记已使用
        verification.is_used = True
        await self.db.commit()
        return True
