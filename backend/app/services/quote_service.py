"""推送编排服务：生成语录 → 渲染邮件 → 发送"""

import asyncio
from datetime import datetime
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Keyword, Mentor, AIModel,
    UserKeywordPref, UserMentorPref, Quote, EmailSendLog,
)
from app.core.quote_engine import QuoteEngine
from app.services.email_sender import EmailSenderPool
from app.utils.email_template import render_daily_quote_email


async def push_for_user(
    user: User,
    db: AsyncSession,
    engine: QuoteEngine,
    sender_pool: EmailSenderPool,
) -> bool:
    """为单个用户执行推送流程：生成 → 保存 → 渲染 → 发送"""
    try:
        # 1. 获取用户可用的关键词
        result = await db.execute(
            select(Keyword).where(
                (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
            )
        )
        keywords = [_orm_to_dict(kw) for kw in result.scalars().all()]

        # 2. 获取用户可用的导师
        result = await db.execute(
            select(Mentor).where(
                (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
            )
        )
        mentors = [_orm_to_dict(m) for m in result.scalars().all()]

        # 3. 获取用户关键词权重
        result = await db.execute(
            select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
        )
        user_kw_weights = {p.keyword_id: p.weight for p in result.scalars().all()}

        # 4. 获取用户启用的导师
        result = await db.execute(
            select(UserMentorPref).where(
                UserMentorPref.user_id == user.id,
                UserMentorPref.is_enabled == True,
            )
        )
        user_mentor_ids = {p.mentor_id for p in result.scalars().all()}
        # 如果没有配置过，None 表示全部启用
        if not user_mentor_ids:
            user_mentor_ids = None

        # 5. 获取活跃的 AI 模型配置
        result = await db.execute(
            select(AIModel).where(AIModel.is_active == True).order_by(AIModel.priority)
        )
        model_configs = [
            {
                "name": m.name,
                "base_url": m.base_url,
                "api_key": m.api_key,
                "model_id": m.model_id,
            }
            for m in result.scalars().all()
        ]

        if not model_configs:
            logger.error(f"用户 {user.email}: 没有可用的 AI 模型")
            return False

        # 6. 生成语录
        quotes = await engine.generate_quotes_for_user(
            user={
                "id": user.id,
                "nickname": user.nickname,
                "age": user.age,
                "mentor_category_prefs": user.mentor_category_prefs,
            },
            keywords=keywords,
            mentors=mentors,
            user_keyword_weights=user_kw_weights,
            user_mentor_ids=user_mentor_ids,
            model_configs=model_configs,
            count=10,
        )

        if not quotes:
            logger.warning(f"用户 {user.email}: 未生成任何语录")
            return False

        # 7. 保存语录到数据库
        for q in quotes:
            quote = Quote(
                user_id=user.id,
                mentor_name=q["mentor_name"],
                mentor_category=q["mentor_category"],
                keyword=q["keyword"],
                content=q["content"],
                ai_model=q["ai_model"],
            )
            db.add(quote)

        # 8. 渲染邮件
        date_str = datetime.now().strftime("%Y年%m月%d日")
        html = render_daily_quote_email(quotes, date_str)
        subject = f"今日人生导师智慧 - {date_str}"

        # 9. 发送邮件
        success, sender_email = await sender_pool.send_via_pool(
            to=user.email, subject=subject, html_content=html,
        )

        # 10. 记录发送日志
        log = EmailSendLog(
            user_id=user.id,
            to_email=user.email,
            sender_email=sender_email,
            subject=subject,
            quote_count=len(quotes),
            status="sent" if success else "failed",
        )
        db.add(log)

        if success:
            user.last_push_date = _today_str()

        await db.commit()

        logger.info(f"用户 {user.email}: 推送{'成功' if success else '失败'} ({len(quotes)}条语录)")
        return success

    except Exception as e:
        logger.error(f"用户 {user.email}: 推送异常 - {e}")
        await db.rollback()
        return False


def _orm_to_dict(obj) -> dict:
    """将 ORM 对象转为字典"""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")
