"""管理后台 - 用户管理"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_admin_user
from app.models import User, EmailSendLog

router = APIRouter()


class AdminUserResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    push_time: str
    push_enabled: bool
    push_count: int
    max_words: int
    personalization_weight: float
    is_active: bool
    is_admin: bool
    created_at: str

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int
    page_size: int


class FailedLogResponse(BaseModel):
    id: int
    user_id: int
    user_email: str
    to_email: str
    sender_email: str
    subject: str
    quote_count: int
    status: str
    error_message: str | None
    retry_count: int
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """用户列表"""
    query = select(User).where(User.is_admin == False)
    count_query = select(func.count()).select_from(User).where(User.is_admin == False)

    if search:
        query = query.where(User.email.contains(search) | User.nickname.contains(search))
        count_query = count_query.where(
            User.email.contains(search) | User.nickname.contains(search)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=[
            AdminUserResponse(
                id=u.id, email=u.email, nickname=u.nickname,
                push_time=u.push_time, push_enabled=u.push_enabled,
                push_count=u.push_count, max_words=u.max_words,
                personalization_weight=u.personalization_weight,
                is_active=u.is_active, is_admin=u.is_admin,
                created_at=u.created_at.isoformat() if u.created_at else "",
            )
            for u in users
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}")
async def get_user_detail(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """用户详情"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "age": user.age,
        "profession": user.profession,
        "personal_bio": user.personal_bio,
        "personalization_weight": user.personalization_weight,
        "push_time": user.push_time,
        "push_enabled": user.push_enabled,
        "push_count": user.push_count,
        "max_words": user.max_words,
        "mentor_category_prefs": user.mentor_category_prefs,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.put("/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """启用/停用用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.is_active = not user.is_active
    await db.commit()
    return {"message": f"用户已{'启用' if user.is_active else '停用'}"}


@router.get("/failed-logs/list")
async def list_failed_logs(
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """获取推送失败的日志列表"""
    count_result = await db.scalar(
        select(func.count()).select_from(EmailSendLog).where(EmailSendLog.status == "failed")
    )
    total = count_result or 0

    result = await db.execute(
        select(EmailSendLog)
        .where(EmailSendLog.status == "failed")
        .order_by(desc(EmailSendLog.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = result.scalars().all()

    # 批量查用户邮箱
    user_ids = list({l.user_id for l in logs})
    user_emails = {}
    if user_ids:
        u_result = await db.execute(select(User.id, User.email).where(User.id.in_(user_ids)))
        user_emails = dict(u_result.all())

    return {
        "items": [
            {
                "id": l.id,
                "user_id": l.user_id,
                "user_email": user_emails.get(l.user_id, ""),
                "to_email": l.to_email,
                "sender_email": l.sender_email,
                "subject": l.subject,
                "quote_count": l.quote_count,
                "status": l.status,
                "error_message": l.error_message,
                "retry_count": l.retry_count,
                "created_at": l.created_at.isoformat() if l.created_at else "",
            }
            for l in logs
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.put("/failed-logs/{log_id}/resolve")
async def resolve_failed_log(
    log_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """标记失败日志为已处理"""
    result = await db.execute(select(EmailSendLog).where(EmailSendLog.id == log_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")

    log.status = "resolved"
    await db.commit()
    return {"message": "已标记为已处理"}
