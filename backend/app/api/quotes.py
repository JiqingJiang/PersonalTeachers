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
    count: int = 3


class TestEmailRequest(BaseModel):
    count: int = 3


def _load_user_mentor_filter(user_id: int, db: AsyncSession):
    """统一的导师开关加载逻辑，与 quote_service 保持一致"""
    return _load_user_mentor_filter_impl(user_id, db)


async def _load_user_mentor_filter_impl(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(UserMentorPref).where(UserMentorPref.user_id == user_id)
    )
    all_prefs = result.scalars().all()
    if all_prefs:
        enabled_ids = {p.mentor_id for p in all_prefs if p.is_enabled}
        disabled_ids = {p.mentor_id for p in all_prefs if not p.is_enabled}
        if disabled_ids:
            # 有禁用记录，用 enabled_ids 做白名单（可以为空集）
            return enabled_ids
        else:
            # 全部启用，不过滤
            return None
    else:
        return None


@router.post("/preview")
async def preview_quotes(
    req: PreviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成预览语录（不保存、不发送）"""
    result = await db.execute(
        select(Keyword).where(
            (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
        )
    )
    keywords = [_orm_to_dict(kw) for kw in result.scalars().all()]

    result = await db.execute(
        select(Mentor).where(
            (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
        )
    )
    mentors = [_orm_to_dict(m) for m in result.scalars().all()]

    result = await db.execute(
        select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
    )
    user_kw_weights = {p.keyword_id: p.weight for p in result.scalars().all()}

    user_mentor_ids = await _load_user_mentor_filter_impl(user.id, db)

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
            "profession": user.profession,
            "mentor_category_prefs": user.mentor_category_prefs,
            "personal_bio": user.personal_bio,
            "personalization_weight": user.personalization_weight,
        },
        keywords=keywords,
        mentors=mentors,
        user_keyword_weights=user_kw_weights,
        user_mentor_ids=user_mentor_ids,
        model_configs=model_configs,
        count=req.count,
        max_words=user.max_words,
    )

    return quotes


@router.post("/test-email")
async def test_email(
    req: TestEmailRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """生成语录并发送测试邮件到用户邮箱"""
    # 复用 preview 逻辑生成语录
    result = await db.execute(
        select(Keyword).where(
            (Keyword.is_system == True) | (Keyword.created_by_user_id == user.id)
        )
    )
    keywords = [_orm_to_dict(kw) for kw in result.scalars().all()]

    result = await db.execute(
        select(Mentor).where(
            (Mentor.is_system == True) | (Mentor.created_by_user_id == user.id)
        )
    )
    mentors = [_orm_to_dict(m) for m in result.scalars().all()]

    result = await db.execute(
        select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
    )
    user_kw_weights = {p.keyword_id: p.weight for p in result.scalars().all()}

    user_mentor_ids = await _load_user_mentor_filter_impl(user.id, db)

    result = await db.execute(
        select(AIModel).where(AIModel.is_active == True).order_by(AIModel.priority)
    )
    model_configs = [
        {"name": m.name, "base_url": m.base_url, "api_key": m.api_key, "model_id": m.model_id}
        for m in result.scalars().all()
    ]

    if not model_configs:
        raise HTTPException(status_code=400, detail="没有可用的 AI 模型")

    from datetime import datetime

    engine = QuoteEngine()
    quotes = await engine.generate_quotes_for_user(
        user={
            "id": user.id,
            "nickname": user.nickname,
            "age": user.age,
            "profession": user.profession,
            "mentor_category_prefs": user.mentor_category_prefs,
            "personal_bio": user.personal_bio,
            "personalization_weight": user.personalization_weight,
        },
        keywords=keywords,
        mentors=mentors,
        user_keyword_weights=user_kw_weights,
        user_mentor_ids=user_mentor_ids,
        model_configs=model_configs,
        count=req.count,
        max_words=user.max_words,
    )

    if not quotes:
        raise HTTPException(status_code=500, detail="未能生成任何语录")

    # 渲染邮件
    from app.utils.email_template import render_daily_quote_email
    date_str = datetime.now().strftime("%Y年%m月%d日")
    html = render_daily_quote_email(quotes, date_str, user_nickname=user.nickname)
    subject = f"[测试] 今日人生导师智慧 - {date_str}"

    # 发送
    from app.services.email_sender import send_email
    success, _ = await send_email(to=user.email, subject=subject, html_content=html)

    if not success:
        raise HTTPException(status_code=500, detail="邮件发送失败，请检查邮箱配置")

    return {"message": f"已发送 {len(quotes)} 条语录到 {user.email}", "quote_count": len(quotes)}


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

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

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
