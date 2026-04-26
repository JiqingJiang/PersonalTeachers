"""管理后台 - 邮箱池管理"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_admin_user
from app.models import User, EmailPool

router = APIRouter()


class EmailPoolResponse(BaseModel):
    id: int
    email: str
    smtp_host: str
    smtp_port: int
    display_name: str
    is_active: bool
    daily_limit: int
    sent_today: int
    last_sent_date: str | None

    model_config = {"from_attributes": True}


class EmailPoolCreate(BaseModel):
    email: str
    smtp_host: str
    smtp_port: int = 587
    smtp_password: str
    display_name: str = "PersonalTeachers"
    daily_limit: int = 200


class EmailPoolUpdate(BaseModel):
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_password: str | None = None
    display_name: str | None = None
    daily_limit: int | None = None
    is_active: bool | None = None


@router.get("/")
async def list_email_pool(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """列出所有发件邮箱"""
    result = await db.execute(select(EmailPool))
    senders = result.scalars().all()

    return [
        {
            "id": s.id,
            "email": s.email,
            "smtp_host": s.smtp_host,
            "smtp_port": s.smtp_port,
            "display_name": s.display_name,
            "is_active": s.is_active,
            "daily_limit": s.daily_limit,
            "sent_today": s.sent_today or 0,
            "last_sent_date": s.last_sent_date,
            "remaining": s.daily_limit - (s.sent_today or 0),
        }
        for s in senders
    ]


@router.post("/", status_code=201)
async def create_email_pool(
    req: EmailPoolCreate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """添加发件邮箱"""
    # 检查是否已存在
    result = await db.execute(select(EmailPool).where(EmailPool.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已存在")

    sender = EmailPool(**req.model_dump())
    db.add(sender)
    await db.commit()
    await db.refresh(sender)
    return {"id": sender.id, "message": "发件邮箱已添加"}


@router.put("/{sender_id}")
async def update_email_pool(
    sender_id: int,
    req: EmailPoolUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """更新发件邮箱"""
    result = await db.execute(select(EmailPool).where(EmailPool.id == sender_id))
    sender = result.scalar_one_or_none()
    if not sender:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(sender, field, value)

    await db.commit()
    return {"message": "发件邮箱已更新"}


@router.delete("/{sender_id}")
async def delete_email_pool(
    sender_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除发件邮箱"""
    result = await db.execute(select(EmailPool).where(EmailPool.id == sender_id))
    sender = result.scalar_one_or_none()
    if not sender:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    await db.delete(sender)
    await db.commit()
    return {"message": "发件邮箱已删除"}


@router.post("/{sender_id}/test")
async def test_email_sender(
    sender_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """测试发件邮箱"""
    result = await db.execute(select(EmailPool).where(EmailPool.id == sender_id))
    sender = result.scalar_one_or_none()
    if not sender:
        raise HTTPException(status_code=404, detail="邮箱不存在")

    from app.services.email_sender import send_email
    success, _ = await send_email(
        to=admin.email,
        subject="PersonalTeachers 邮箱测试",
        html_content="<h2>邮箱测试成功</h2><p>该邮箱可以正常发送邮件。</p>",
        smtp_host=sender.smtp_host,
        smtp_port=sender.smtp_port,
        smtp_username=sender.email,
        smtp_password=sender.smtp_password,
    )

    if success:
        return {"message": "测试邮件发送成功"}
    else:
        raise HTTPException(status_code=500, detail="测试邮件发送失败")
