"""推送编排服务：生成语录 → 渲染邮件 → 发送"""

import asyncio
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Keyword, Mentor, AIModel,
    UserKeywordPref, UserMentorPref, Quote, EmailSendLog, EmailPool,
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
    """为单个用户执行推送流程：生成 → 保存 → 渲染 → 发送

    所有失败场景都会写入 EmailSendLog 并附带 error_message。
    """
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

        # 4. 获取用户的导师偏好（包含启用和禁用）
        result = await db.execute(
            select(UserMentorPref).where(UserMentorPref.user_id == user.id)
        )
        all_prefs = result.scalars().all()
        if all_prefs:
            enabled_ids = {p.mentor_id for p in all_prefs if p.is_enabled}
            disabled_ids = {p.mentor_id for p in all_prefs if not p.is_enabled}
            if disabled_ids:
                user_mentor_ids = enabled_ids
            else:
                user_mentor_ids = None
        else:
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
            error_msg = "没有可用的 AI 模型配置，请在管理后台添加并启用至少一个模型"
            logger.error(f"用户 {user.email}: {error_msg}")
            await _log_failure(db, user, sender_pool, 0, error_msg)
            return False

        # 6. 获取近期语录内容用于去重（最近2天的）
        recent_cutoff = datetime.now() - timedelta(days=2)
        result = await db.execute(
            select(Quote.content).where(
                Quote.user_id == user.id,
                Quote.created_at >= recent_cutoff,
            ).order_by(Quote.created_at.desc()).limit(30)
        )
        recent_contents = [row[0] for row in result.all()]

        # 7. 生成语录（使用用户设定的数量和字数限制）
        quotes = await engine.generate_quotes_for_user(
            user={
                "id": user.id,
                "nickname": user.nickname,
                "age": user.age,
                "profession": user.profession,
                "mentor_category_prefs": user.mentor_category_prefs,
                "personal_bio": user.personal_bio,
                "personalization_weight": user.personalization_weight,
            },
            keywords=keywords,
            mentors=mentors,
            user_keyword_weights=user_kw_weights,
            user_mentor_ids=user_mentor_ids,
            model_configs=model_configs,
            count=user.push_count,
            max_words=user.max_words,
            recent_contents=recent_contents,
        )

        if not quotes:
            error_msg = "AI 模型未生成任何语录（可能因内容质量校验未通过或模型返回为空）"
            logger.warning(f"用户 {user.email}: {error_msg}")
            await _log_failure(db, user, sender_pool, 0, error_msg)
            return False

        # 8. 保存语录到数据库
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

        # 9. 渲染邮件
        date_str = datetime.now().strftime("%Y年%m月%d日")
        html = render_daily_quote_email(quotes, date_str, user_nickname=user.nickname)
        subject = f"今日人生导师智慧 - {date_str}"

        # 10. 发送邮件
        success, sender_email, error_message = await sender_pool.send_via_pool(
            to=user.email, subject=subject, html_content=html,
        )

        # 11. 记录发送日志
        log = EmailSendLog(
            user_id=user.id,
            to_email=user.email,
            sender_email=sender_email,
            subject=subject,
            quote_count=len(quotes),
            status="sent" if success else "failed",
            error_message=error_message if not success else None,
        )
        db.add(log)

        if success:
            user.last_push_date = _today_str()
            await _update_sender_count(db, sender_email)

        await db.commit()

        logger.info(f"用户 {user.email}: 推送{'成功' if success else '失败'} ({len(quotes)}条语录)")
        return success

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error(f"用户 {user.email}: 推送异常 - {error_msg}")
        await db.rollback()
        try:
            await _log_failure(db, user, sender_pool, 0, error_msg)
        except Exception:
            logger.error(f"用户 {user.email}: 写入失败日志也异常")
        return False


def _orm_to_dict(obj) -> dict:
    """将 ORM 对象转为字典"""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


async def _log_failure(
    db: AsyncSession,
    user: User,
    sender_pool: EmailSenderPool,
    quote_count: int,
    error_message: str,
):
    """将推送失败记录写入 EmailSendLog"""
    sender = sender_pool.get_next_sender() if sender_pool else None
    log = EmailSendLog(
        user_id=user.id,
        to_email=user.email,
        sender_email=sender["email"] if sender else "",
        subject="",
        quote_count=quote_count,
        status="failed",
        error_message=error_message,
    )
    db.add(log)
    await db.commit()


async def _update_sender_count(db: AsyncSession, sender_email: str):
    """推送成功后回写邮箱池的 sent_today 计数到数据库"""
    if not sender_email:
        return
    result = await db.execute(select(EmailPool).where(EmailPool.email == sender_email))
    sender = result.scalar_one_or_none()
    if sender:
        today = _today_str()
        if sender.last_sent_date != today:
            sender.sent_today = 1
            sender.last_sent_date = today
        else:
            sender.sent_today = (sender.sent_today or 0) + 1
