"""数据清理服务：定期清理过期数据"""

from datetime import datetime, timezone, timedelta
from loguru import logger
from sqlalchemy import delete

from app.models import Quote, EmailSendLog, VerificationCode
from app.models import database as db_module
from app.models.database import init_db


async def cleanup_expired_data():
    """清理30天前的语录、发送日志和过期验证码"""
    if db_module.async_session is None:
        await init_db()

    # SQLite 存储的 datetime 是 naive 的，比较时也要用 naive
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with db_module.async_session() as db:
        # 清理过期语录
        result = await db.execute(
            delete(Quote).where(Quote.created_at < cutoff)
        )
        quotes_deleted = result.rowcount

        # 清理过期发送日志
        result = await db.execute(
            delete(EmailSendLog).where(EmailSendLog.created_at < cutoff)
        )
        logs_deleted = result.rowcount

        # 清理过期验证码
        result = await db.execute(
            delete(VerificationCode).where(VerificationCode.expires_at < now)
        )
        codes_deleted = result.rowcount

        await db.commit()

    logger.info(
        f"数据清理完成: 语录 {quotes_deleted} 条, "
        f"日志 {logs_deleted} 条, 验证码 {codes_deleted} 条"
    )
