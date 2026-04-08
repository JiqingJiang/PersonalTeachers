"""语录 API"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User, Quote, Keyword, Mentor, AIModel, UserKeywordPref, UserMentorPref
from app.core.quote_engine import QuoteEngine

router = APIRouter()


class QuoteResponse(BaseModel):
    id: int
    mentor_name: str
    mentor_category: str
    keyword: str
    content: str
    ai_model: str
    created_at: str

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    items: list[QuoteResponse]
    total: int
    page: int
    page_size: int


class PreviewRequest(BaseModel):
    count: int = 3  # 预览条数，默认3


@router.post("/preview")
async def preview_quotes(
    req: PreviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成预览语录（不保存、不发送）"""
    # 获取用户可用的关键词
    result = await db.execute(
        select(Keyword).where(
            (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
        )
    )
    keywords = [_orm_to_dict(kw) for kw in result.scalars().all()]

    # 获取用户可用的导师
    result = await db.execute(
        select(Mentor).where(
            (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
        )
    )
    mentors = [_orm_to_dict(m) for m in result.scalars().all()]

    # 获取用户关键词权重
    result = await db.execute(
        select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
    )
    user_kw_weights = {p.keyword_id: p.weight for p in result.scalars().all()}

    # 获取用户启用的导师
    result = await db.execute(
        select(UserMentorPref).where(
            UserMentorPref.user_id == user.id,
            UserMentorPref.is_enabled == True,
        )
    )
    user_mentor_ids = {p.mentor_id for p in result.scalars().all()} or None

    # 获取 AI 模型配置
    result = await db.execute(
        select(AIModel).where(AIModel.is_active == True).order_by(AIModel.priority)
    )
    model_configs = [
        {"name": m.name, "base_url": m.base_url, "api_key": m.api_key, "model_id": m.model_id}
        for m in result.scalars().all()
    ]

    if not model_configs:
        raise HTTPException(status_code=400, detail="没有可用的 AI 模型，请在管理后台配置")

    engine = QuoteEngine()
    quotes = await engine.generate_quotes_for_user(
        user={
            "id": user.id,
            "nickname": user.nickname,
            "age": user.age,
            "mentor_category_prefs": user.mentor_category_prefs,
        },
        keywords=keywords,
        mentors=mentors,
        user_keyword_weights=user_kw_weights,
        user_mentor_ids=user_mentor_ids,
        model_configs=model_configs,
        count=req.count,
    )

    return quotes


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户历史语录（分页）"""
    query = select(Quote).where(Quote.user_id == user.id)
    count_query = select(func.count()).select_from(Quote).where(Quote.user_id == user.id)

    if keyword:
        query = query.where(Quote.keyword == keyword)
        count_query = count_query.where(Quote.keyword == keyword)

    # 总数
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页查询
    query = query.order_by(desc(Quote.created_at)).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    quotes = result.scalars().all()

    return HistoryResponse(
        items=[
            QuoteResponse(
                id=q.id,
                mentor_name=q.mentor_name,
                mentor_category=q.mentor_category,
                keyword=q.keyword,
                content=q.content,
                ai_model=q.ai_model,
                created_at=q.created_at.isoformat() if q.created_at else "",
            )
            for q in quotes
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


def _orm_to_dict(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
