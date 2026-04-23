"""偏好设置 API"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models import User, Keyword, Mentor, UserKeywordPref, UserMentorPref

router = APIRouter()


class PushSettings(BaseModel):
    push_time: str | None = None  # HH:MM
    push_enabled: bool | None = None
    push_count: int | None = Field(None, ge=1, le=10)
    max_words: int | None = Field(None, ge=30, le=200)


class KeywordWeightUpdate(BaseModel):
    weights: dict[int, float]  # {keyword_id: weight}


class MentorPrefUpdate(BaseModel):
    mentors: list[dict]  # [{"mentor_id": 1, "is_enabled": true}, ...]


class CategoryWeightUpdate(BaseModel):
    historical: float = 0.3
    modern: float = 0.4
    common: float = 0.1
    future_self: float = 0.2


class PreferencesResponse(BaseModel):
    push_time: str
    push_enabled: bool
    push_count: int
    max_words: int
    personalization_weight: float
    mentor_category_prefs: dict
    keyword_weights: dict  # {keyword_id: weight}
    mentor_prefs: dict  # {mentor_id: is_enabled}


@router.get("/")
async def get_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户完整偏好"""
    # 关键词权重
    result = await db.execute(
        select(UserKeywordPref).where(UserKeywordPref.user_id == user.id)
    )
    kw_prefs = {str(p.keyword_id): p.weight for p in result.scalars().all()}

    # 导师偏好
    result = await db.execute(
        select(UserMentorPref).where(UserMentorPref.user_id == user.id)
    )
    mentor_prefs = {str(p.mentor_id): p.is_enabled for p in result.scalars().all()}

    return {
        "push_time": user.push_time,
        "push_enabled": user.push_enabled,
        "push_count": user.push_count,
        "max_words": user.max_words,
        "personalization_weight": user.personalization_weight,
        "mentor_category_prefs": user.mentor_category_prefs or {},
        "keyword_weights": kw_prefs,
        "mentor_prefs": mentor_prefs,
    }


@router.put("/push")
async def update_push_settings(
    req: PushSettings,
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新推送设置"""
    if req.push_time is not None:
        # 验证时间格式 HH:MM
        try:
            parts = req.push_time.split(":")
            assert len(parts) == 2
            assert 0 <= int(parts[0]) <= 23 and 0 <= int(parts[1]) <= 59
        except (ValueError, AssertionError):
            return {"error": "时间格式错误，应为 HH:MM"}
        user.push_time = req.push_time

    if req.push_enabled is not None:
        user.push_enabled = req.push_enabled

    if req.push_count is not None:
        user.push_count = req.push_count

    if req.max_words is not None:
        user.max_words = req.max_words

    await db.commit()

    # 立即刷新调度器
    scheduler = getattr(request.app.state, "scheduler", None)
    if scheduler:
        scheduler.refresh()

    return {"message": "推送设置已更新"}


@router.put("/keyword-weights")
async def update_keyword_weights(
    req: KeywordWeightUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量更新关键词权重"""
    for keyword_id, weight in req.weights.items():
        result = await db.execute(
            select(UserKeywordPref).where(
                UserKeywordPref.user_id == user.id,
                UserKeywordPref.keyword_id == keyword_id,
            )
        )
        pref = result.scalar_one_or_none()
        if pref:
            pref.weight = weight
        else:
            db.add(UserKeywordPref(
                user_id=user.id, keyword_id=keyword_id, weight=weight
            ))

    await db.commit()
    return {"message": f"已更新 {len(req.weights)} 个关键词权重"}


@router.put("/mentor-prefs")
async def update_mentor_prefs(
    req: MentorPrefUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """批量更新导师偏好（启用/禁用）"""
    for item in req.mentors:
        mentor_id = item["mentor_id"]
        is_enabled = item.get("is_enabled", True)

        result = await db.execute(
            select(UserMentorPref).where(
                UserMentorPref.user_id == user.id,
                UserMentorPref.mentor_id == mentor_id,
            )
        )
        pref = result.scalar_one_or_none()
        if pref:
            pref.is_enabled = is_enabled
        else:
            db.add(UserMentorPref(
                user_id=user.id, mentor_id=mentor_id, is_enabled=is_enabled
            ))

    await db.commit()
    return {"message": f"已更新 {len(req.mentors)} 个导师偏好"}


@router.put("/category-weights")
async def update_category_weights(
    req: CategoryWeightUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新导师类别权重"""
    user.mentor_category_prefs = req.model_dump()
    await db.commit()
    return {"message": "类别权重已更新"}
