"""管理后台 - AI 模型配置"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_admin_user
from app.models import User, AIModel

router = APIRouter()


class AIModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    base_url: str
    api_key: str  # 列表中返回，管理后台需要显示
    model_id: str
    priority: int
    is_active: bool
    max_tokens: int
    temperature: float

    model_config = {"from_attributes": True}


class AIModelCreate(BaseModel):
    name: str
    provider: str  # deepseek / zhipu / custom
    base_url: str
    api_key: str
    model_id: str
    priority: int = 1
    is_active: bool = True
    max_tokens: int = 300
    temperature: float = 0.7


class AIModelUpdate(BaseModel):
    name: str | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_id: str | None = None
    priority: int | None = None
    is_active: bool | None = None
    max_tokens: int | None = None
    temperature: float | None = None


@router.get("/")
async def list_ai_models(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """列出所有 AI 模型配置"""
    result = await db.execute(select(AIModel).order_by(AIModel.priority))
    models = result.scalars().all()

    # 隐藏 api_key 中间部分
    items = []
    for m in models:
        d = {
            "id": m.id, "name": m.name, "provider": m.provider,
            "base_url": m.base_url, "model_id": m.model_id,
            "priority": m.priority, "is_active": m.is_active,
            "max_tokens": m.max_tokens, "temperature": m.temperature,
            "api_key": m.api_key[:8] + "..." + m.api_key[-4:] if len(m.api_key) > 12 else m.api_key,
            "has_api_key": bool(m.api_key),
        }
        items.append(d)
    return items


@router.post("/", status_code=201)
async def create_ai_model(
    req: AIModelCreate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """新增 AI 模型"""
    model = AIModel(**req.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return {"id": model.id, "message": "AI 模型已创建"}


@router.put("/{model_id}")
async def update_ai_model(
    model_id: int,
    req: AIModelUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 AI 模型配置"""
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(model, field, value)

    await db.commit()
    return {"message": "AI 模型已更新"}


@router.delete("/{model_id}")
async def delete_ai_model(
    model_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 AI 模型"""
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    await db.delete(model)
    await db.commit()
    return {"message": "AI 模型已删除"}
