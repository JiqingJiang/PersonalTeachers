"""认证 API"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User
from app.services.verification import VerificationService
from app.services.email_sender import send_verification_code_email
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter()


# --- Request/Response Models ---

class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: str  # register / reset_password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    code: str
    nickname: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    is_admin: bool

    model_config = {"from_attributes": True}


# --- Endpoints ---

@router.post("/send-code")
async def send_code(req: SendCodeRequest, db: AsyncSession = Depends(get_db)):
    """发送邮箱验证码"""
    # 注册时检查邮箱是否已存在
    if req.purpose == "register":
        result = await db.execute(select(User).where(User.email == req.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该邮箱已注册")

    # 重置密码时检查邮箱是否存在
    if req.purpose == "reset_password":
        result = await db.execute(select(User).where(User.email == req.email))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该邮箱未注册")

    svc = VerificationService(db)
    code = await svc.create_code(req.email, req.purpose)

    success = await send_verification_code_email(req.email, code)
    if not success:
        # 开发环境直接返回验证码（生产环境应移除）
        from app.config import get_settings
        settings = get_settings()
        if settings.DEBUG:
            return {"message": "验证码已生成（调试模式）", "code": code}
        raise HTTPException(status_code=500, detail="验证码发送失败")

    return {"message": "验证码已发送"}


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 验证验证码
    svc = VerificationService(db)
    if not await svc.validate_code(req.email, req.code, "register"):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")

    # 创建用户
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.email.split("@")[0],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """登录"""
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已停用")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh")
async def refresh_token(req: RefreshRequest):
    """刷新 access token"""
    payload = decode_token(req.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="无效的 refresh token")

    return {"access_token": create_access_token(int(payload["sub"])), "token_type": "bearer"}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """重置密码"""
    svc = VerificationService(db)
    if not await svc.validate_code(req.email, req.code, "reset_password"):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(req.new_password)
    await db.commit()

    return {"message": "密码重置成功"}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return user
