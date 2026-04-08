"""导师 API"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User, Mentor, UserMentorPref

router = APIRouter()


class MentorResponse(BaseModel):
    id: int
    name: str
    category: str
    field: str | None
    perspective: str | None
    keywords: list | None
    personality: str | None
    tone: str | None
    background: str | None
    era: str | None
    peak_stage: str | None
    years_ahead: int | None
    is_system: bool
    is_enabled: bool | None = None  # 用户是否启用

    model_config = {"from_attributes": True}


class MentorCreate(BaseModel):
    name: str
    category: str  # historical/modern/common/future_self
    field: str | None = None
    perspective: str | None = None
    keywords: list[str] | None = None
    personality: str | None = None
    tone: str | None = None
    background: str | None = None
    years_ahead: int | None = None


class MentorUpdate(BaseModel):
    name: str | None = None
    field: str | None = None
    perspective: str | None = None
    keywords: list[str] | None = None
    personality: str | None = None
    tone: str | None = None
    background: str | None = None


@router.get("/")
async def list_mentors(
    category: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出所有可用导师（系统 + 用户自定义），附带启用状态"""
    # 获取用户的导师偏好
    result = await db.execute(
        select(UserMentorPref).where(UserMentorPref.user_id == user.id)
    )
    prefs = {p.mentor_id: p.is_enabled for p in result.scalars().all()}

    # 查询导师
    query = select(Mentor).where(
        (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
    )
    if category:
        query = query.where(Mentor.category == category)
    query = query.order_by(Mentor.category, Mentor.id)

    result = await db.execute(query)
    mentors = result.scalars().all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "field": m.field,
            "perspective": m.perspective,
            "keywords": m.keywords,
            "personality": m.personality,
            "tone": m.tone,
            "background": m.background,
            "era": m.era,
            "peak_stage": m.peak_stage,
            "years_ahead": m.years_ahead,
            "is_system": m.is_system,
            "is_enabled": prefs.get(m.id, True),  # 默认启用
        }
        for m in mentors
    ]


@router.get("/categories")
async def list_categories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取导师类别概要"""
    categories = [
        {"id": "historical", "name": "历史人物", "emoji": "📜"},
        {"id": "modern", "name": "现代人物", "emoji": "💼"},
        {"id": "common", "name": "普通百姓", "emoji": "👥"},
        {"id": "future_self", "name": "未来自己", "emoji": "🔮"},
    ]

    result = await db.execute(
        select(Mentor).where(
            (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
        )
    )
    all_mentors = result.scalars().all()

    for c in categories:
        c["count"] = sum(1 for m in all_mentors if m.category == c["id"])

    return categories


@router.post("/", response_model=MentorResponse, status_code=status.HTTP_201_CREATED)
async def create_mentor(
    req: MentorCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """新增自定义导师"""
    mentor = Mentor(
        name=req.name,
        category=req.category,
        field=req.field,
        perspective=req.perspective,
        keywords=req.keywords,
        personality=req.personality,
        tone=req.tone,
        background=req.background,
        years_ahead=req.years_ahead,
        is_system=False,
        created_by_user_id=user.id,
    )
    db.add(mentor)
    await db.commit()
    await db.refresh(mentor)
    return mentor


@router.put("/custom/{mentor_id}", response_model=MentorResponse)
async def update_custom_mentor(
    mentor_id: int,
    req: MentorUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改自定义导师"""
    result = await db.execute(
        select(Mentor).where(
            Mentor.id == mentor_id,
            Mentor.created_by_user_id == user.id,
            Mentor.is_system == False,
        )
    )
    mentor = result.scalar_one_or_none()
    if not mentor:
        raise HTTPException(status_code=404, detail="导师不存在")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(mentor, field, value)

    await db.commit()
    await db.refresh(mentor)
    return mentor


@router.delete("/custom/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_mentor(
    mentor_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除自定义导师"""
    result = await db.execute(
        select(Mentor).where(
            Mentor.id == mentor_id,
            Mentor.created_by_user_id == user.id,
            Mentor.is_system == False,
        )
    )
    mentor = result.scalar_one_or_none()
    if not mentor:
        raise HTTPException(status_code=404, detail="导师不存在")

    await db.delete(mentor)
    await db.commit()
