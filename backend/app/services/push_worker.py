"""RQ Worker 推送任务执行逻辑

被 RQ Worker 调用的同步函数，内部用 asyncio.run 包装 async 操作。
"""

import asyncio
from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import select

from app.models import (
    User, Keyword, Mentor, AIModel,
    UserKeywordPref, UserMentorPref, Quote, EmailSendLog, EmailPool,
)
from app.models.database import init_db, async_session
from app.core.quote_engine import QuoteEngine
from app.services.email_sender import EmailSenderPool
from app.utils.email_template import render_daily_quote_email


def execute_push(user_id: int) -> bool:
    """RQ 任务入口：为单个用户执行推送（同步包装）"""
    return asyncio.run(_execute_push_async(user_id))


async def _execute_push_async(user_id: int) -> bool:
    """异步推送实现"""
    await init_db()

    async with async_session() as db:
        try:
            user = await db.get(User, user_id)
            if not user:
                logger.error(f"用户 {user_id} 不存在")
                return False

            # 1. 获取关键词
            result = await db.execute(
                __user_keywords_query(user_id)
            )
            keywords = [_orm_to_dict(kw) for kw in result.scalars().all()]

            # 2. 获取导师
            result = await db.execute(
                __user_mentors_query(user_id)
            )
            mentors = [_orm_to_dict(m) for m in result.scalars().all()]

            # 3. 获取关键词权重
            result = await db.execute(
                UserKeywordPref.__table__.select().where(UserKeywordPref.user_id == user_id)
            )
            kw_weights = {p.keyword_id: p.weight for p in result.scalars().all()}

            # 4. 获取导师偏好
            result = await db.execute(
                UserMentorPref.__table__.select().where(UserMentorPref.user_id == user_id)
            )
            user_mentor_ids = _resolve_mentor_ids(result.scalars().all())

            # 5. 获取 AI 模型
            result = await db.execute(
                AIModel.__table__.select()
                .where(AIModel.is_active == True)
                .order_by(AIModel.priority)
            )
            model_configs = [
                {"name": m.name, "base_url": m.base_url, "api_key": m.api_key, "model_id": m.model_id}
                for m in result.scalars().all()
            ]
            if not model_configs:
                await _log_failure(db, user_id, "没有可用的 AI 模型")
                return False

            # 6. 获取近期语录去重
            recent_cutoff = datetime.now() - timedelta(days=2)
            result = await db.execute(
                Quote.__table__.select()
                .where(Quote.user_id == user_id, Quote.created_at >= recent_cutoff)
                .order_by(Quote.created_at.desc())
                .limit(30)
            )
            recent_contents = [row[0] for row in result.all()]

            # 7. 生成语录
            engine = QuoteEngine()
            quotes = await engine.generate_quotes_for_user(
                user={
                    "id": user.id, "nickname": user.nickname, "age": user.age,
                    "profession": user.profession,
                    "mentor_category_prefs": user.mentor_category_prefs,
                    "personal_bio": user.personal_bio,
                    "personalization_weight": user.personalization_weight,
                },
                keywords=keywords, mentors=mentors,
                user_keyword_weights=kw_weights,
                user_mentor_ids=user_mentor_ids,
                model_configs=model_configs,
                count=user.push_count, max_words=user.max_words,
                recent_contents=recent_contents,
            )

            if not quotes:
                await _log_failure(db, user_id, "未生成任何语录")
                return False

            # 8. 保存语录
            for q in quotes:
                db.add(Quote(
                    user_id=user.id, mentor_name=q["mentor_name"],
                    mentor_category=q["mentor_category"], keyword=q["keyword"],
                    content=q["content"], ai_model=q["ai_model"],
                ))

            # 9. 渲染并发送邮件
            date_str = datetime.now().strftime("%Y年%m月%d日")
            html = render_daily_quote_email(quotes, date_str, user_nickname=user.nickname)
            subject = f"今日人生导师智慧 - {date_str}"

            sender_pool = await _load_sender_pool()
            success, sender_email = await sender_pool.send_via_pool(
                to=user.email, subject=subject, html_content=html,
            )

            # 10. 写发送日志（补全 error_message）
            log = EmailSendLog(
                user_id=user.id, to_email=user.email,
                sender_email=sender_email or "", subject=subject,
                quote_count=len(quotes),
                status="sent" if success else "failed",
                error_message=None if success else "邮件发送失败",
            )
            db.add(log)

            if success:
                user.last_push_date = datetime.now().strftime("%Y-%m-%d")
                await _update_sender_count(db, sender_email)

            await db.commit()
            logger.info(f"用户 {user.email}: 推送{'成功' if success else '失败'}")
            return success

        except Exception as e:
            logger.error(f"用户 {user_id}: 推送异常 - {e}")
            await db.rollback()
            # RQ retry 时会再次调用此函数，这里记录失败原因
            try:
                await _log_failure(db, user_id, str(e))
            except Exception:
                pass
            raise  # 重新抛出让 RQ 触发 retry


def _orm_to_dict(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _resolve_mentor_ids(prefs) -> set[int] | None:
    if not prefs:
        return None
    disabled_ids = {p.mentor_id for p in prefs if not p.is_enabled}
    if disabled_ids:
        return {p.mentor_id for p in prefs if p.is_enabled}
    return None


def _user_keywords_query(user_id: int):
    return select(Keyword).where(
        (Keyword.is_system == True) | (Keyword.created_by_user_id == user_id)
    )


def _user_mentors_query(user_id: int):
    return select(Mentor).where(
        (Mentor.is_system == True) | (Mentor.created_by_user_id == user_id)
    )


async def _load_sender_pool() -> EmailSenderPool:
    async with async_session() as db:
        result = await db.execute(
            select(EmailPool).where(EmailPool.is_active == True)
        )
    senders = [
        {
            "email": s.email, "smtp_host": s.smtp_host, "smtp_port": s.smtp_port,
            "smtp_password": s.smtp_password, "display_name": s.display_name,
            "daily_limit": s.daily_limit, "sent_today": s.sent_today or 0,
            "last_sent_date": s.last_sent_date,
        }
        for s in result.scalars().all()
    ]
    return EmailSenderPool(senders)


async def _update_sender_count(db, sender_email: str):
    if not sender_email:
        return
    result = await db.execute(select(EmailPool).where(EmailPool.email == sender_email))
    sender = result.scalar_one_or_none()
    if sender:
        today = datetime.now().strftime("%Y-%m-%d")
        if sender.last_sent_date != today:
            sender.sent_today = 1
            sender.last_sent_date = today
        else:
            sender.sent_today = (sender.sent_today or 0) + 1


async def _log_failure(db, user_id: int, error_msg: str):
    user = await db.get(User, user_id)
    db.add(EmailSendLog(
        user_id=user_id,
        to_email=user.email if user else "",
        sender_email="",
        subject="推送失败",
        quote_count=0,
        status="failed",
        error_message=error_msg,
    ))
    await db.commit()
