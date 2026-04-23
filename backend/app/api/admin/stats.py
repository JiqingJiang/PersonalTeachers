"""管理后台 - 统计看板"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_admin_user
from app.models import User, Quote, EmailSendLog

router = APIRouter()


@router.get("/dashboard")
async def dashboard(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """管理后台首页统计数据"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    # 总用户数
    total_users = await db.scalar(
        select(func.count()).select_from(User).where(User.is_admin == False)
    )

    # 今日活跃用户（有推送记录的）
    active_today = await db.scalar(
        select(func.count()).select_from(User).where(
            User.is_admin == False,
            User.last_push_date == today,
        )
    )

    # 今日推送统计
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs = await db.execute(
        select(EmailSendLog).where(EmailSendLog.created_at >= today_start)
    )
    logs = today_logs.scalars().all()

    sent_today = sum(1 for l in logs if l.status == "sent")
    failed_today = sum(1 for l in logs if l.status == "failed")

    # 本周新增用户
    week_ago = now - timedelta(days=7)
    new_this_week = await db.scalar(
        select(func.count()).select_from(User).where(
            User.is_admin == False,
            User.created_at >= week_ago,
        )
    )

    return {
        "total_users": total_users or 0,
        "active_today": active_today or 0,
        "new_this_week": new_this_week or 0,
        "sent_today": sent_today,
        "failed_today": failed_today,
        "success_rate": round(sent_today / max(sent_today + failed_today, 1) * 100, 1),
    }


@router.get("/push")
async def push_stats(
    days: int = 7,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """推送统计（按天）"""
    since = datetime.now() - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(EmailSendLog.created_at).label("date"),
            func.count().label("total"),
            func.sum(func.cast(EmailSendLog.status == "sent", Integer)).label("sent"),
            func.sum(func.cast(EmailSendLog.status == "failed", Integer)).label("failed"),
        )
        .where(EmailSendLog.created_at >= since)
        .group_by(func.date(EmailSendLog.created_at))
        .order_by(func.date(EmailSendLog.created_at))
    )

    return [
        {
            "date": str(row.date),
            "total": row.total,
            "sent": row.sent or 0,
            "failed": row.failed or 0,
        }
        for row in result.all()
    ]


@router.get("/email")
async def email_stats(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """邮件发送量统计（按发件邮箱）"""
    from app.models import EmailPool
    result = await db.execute(select(EmailPool))
    senders = result.scalars().all()

    return [
        {
            "email": s.email,
            "daily_limit": s.daily_limit,
            "sent_today": s.sent_today or 0,
            "remaining": s.daily_limit - (s.sent_today or 0),
            "is_active": s.is_active,
        }
        for s in senders
    ]


# 需要导入 Integer
from sqlalchemy import Integer
