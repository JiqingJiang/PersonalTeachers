"""关键词 API"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User, Keyword, UserKeywordPref

router = APIRouter()


class KeywordResponse(BaseModel):
    id: int
    name: str
    english: str | None
    quadrant: int
    category: str | None
    description: str | None
    default_weight: float
    is_system: bool
    weight: float | None = None  # 用户自定义权重

    model_config = {"from_attributes": True}


class KeywordCreate(BaseModel):
    name: str
    english: str | None = None
    quadrant: int = 1
    category: str | None = None
    description: str | None = None


class KeywordUpdate(BaseModel):
    name: str | None = None
    english: str | None = None
    quadrant: int | None = None
    category: str | None = None
    description: str | None = None


@router.get("/")
async def list_keywords(
    quadrant: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出所有可用关键词（系统 + 用户自定义），附带用户权重"""
    # 获取用户的权重配置
    result = await db.execute(
        select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
    )
    prefs = {p.keyword_id: p.weight for p in result.scalars().all()}

    # 查询关键词
    query = select(Keyword).where(
        (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
    )
    if quadrant:
        query = query.where(Keyword.quadrant == quadrant)
    query = query.order_by(Keyword.quadrant, Keyword.id)

    result = await db.execute(query)
    keywords = result.scalars().all()

    return [
        {
            "id": kw.id,
            "name": kw.name,
            "english": kw.english,
            "quadrant": kw.quadrant,
            "category": kw.category,
            "description": kw.description,
            "default_weight": kw.default_weight,
            "is_system": kw.is_system,
            "weight": prefs.get(kw.id),
        }
        for kw in keywords
    ]


@router.get("/quadrants")
async def list_quadrants(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取4个象限的概要信息"""
    quadrants = [
        {"id": 1, "name": "生存与根基", "english": "Foundation", "emoji": "🏠"},
        {"id": 2, "name": "关系与情感", "english": "Connection", "emoji": "❤️"},
        {"id": 3, "name": "成长与认知", "english": "Growth", "emoji": "🌱"},
        {"id": 4, "name": "终极与哲思", "english": "Ultimate", "emoji": "🌌"},
    ]

    result = await db.execute(
        select(Keyword).where(
            (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
        )
    )
    all_keywords = result.scalars().all()

    for q in quadrants:
        q["count"] = sum(1 for kw in all_keywords if kw.quadrant == q["id"])

    return quadrants


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    req: KeywordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """新增自定义关键词"""
    keyword = Keyword(
        name=req.name,
        english=req.english,
        quadrant=req.quadrant,
        category=req.category,
        description=req.description,
        is_system=False,
        created_by_user_id=user.id,
    )
    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)
    return keyword


@router.put("/custom/{keyword_id}", response_model=KeywordResponse)
async def update_custom_keyword(
    keyword_id: int,
    req: KeywordUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """修改自定义关键词"""
    result = await db.execute(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.created_by_user_id == user.id,
            Keyword.is_system == False,
        )
    )
    keyword = result.scalar_one_or_none()
    if not keyword:
        raise HTTPException(status_code=404, detail="关键词不存在")

    if req.name is not None:
        keyword.name = req.name
    if req.english is not None:
        keyword.english = req.english
    if req.quadrant is not None:
        keyword.quadrant = req.quadrant
    if req.category is not None:
        keyword.category = req.category
    if req.description is not None:
        keyword.description = req.description

    await db.commit()
    await db.refresh(keyword)
    return keyword


@router.delete("/custom/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_keyword(
    keyword_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除自定义关键词"""
    result = await db.execute(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.created_by_user_id == user.id,
            Keyword.is_system == False,
        )
    )
    keyword = result.scalar_one_or_none()
    if not keyword:
        raise HTTPException(status_code=404, detail="关键词不存在")

    await db.delete(keyword)
    await db.commit()
