"""用户 API"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User
from app.utils.security import hash_password, verify_password

router = APIRouter()


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    age: int | None = None
    profession: str | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class ProfileResponse(BaseModel):
    id: int
    email: str
    nickname: str | None
    age: int | None
    profession: str | None
    push_time: str
    push_enabled: bool

    model_config = {"from_attributes": True}


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return user


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    req: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.age is not None:
        user.age = req.age
    if req.profession is not None:
        user.profession = req.profession
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/password")
async def change_password(
    req: PasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    user.password_hash = hash_password(req.new_password)
    await db.commit()
    return {"message": "密码修改成功"}
