"""
导师相关API端点

提供导师列表、查询等功能
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from loguru import logger

from app.models.database import Mentor
from app.core import get_mentor_pool


router = APIRouter(prefix="/api/mentors", tags=["导师"])


@router.get("", response_model=List[Mentor])
async def get_all_mentors(
    category: Optional[str] = Query(None, description="按类别筛选"),
    keyword: Optional[str] = Query(None, description="按擅长关键词筛选")
):
    """
    获取所有导师列表

    支持按类别和关键词筛选
    """
    try:
        mentor_pool = get_mentor_pool()

        if category:
            from app.models.database import MentorCategory
            mentors = mentor_pool.get_mentors_by_category(MentorCategory(category))
        elif keyword:
            mentors = mentor_pool.get_mentors_by_keyword(keyword)
        else:
            mentors = mentor_pool.get_all_mentors()

        return mentors

    except Exception as e:
        logger.error(f"Error fetching mentors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mentor_id}", response_model=Mentor)
async def get_mentor_by_id(mentor_id: str):
    """
    获取单个导师详情
    """
    try:
        mentor_pool = get_mentor_pool()
        mentor = mentor_pool.get_mentor_by_id(mentor_id)

        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")

        return mentor

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mentor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_mentors():
    """
    重新加载导师池配置

    修改 mentors.yaml 后调用此接口，无需重启应用
    """
    try:
        mentor_pool = get_mentor_pool()
        old_count = len(mentor_pool.get_all_mentors())
        mentor_pool.reload()
        new_count = len(mentor_pool.get_all_mentors())

        logger.info(f"Mentor pool reloaded: {old_count} -> {new_count} mentors")

        return {
            "success": True,
            "message": f"导师池已重新加载: {old_count} -> {new_count} 位导师",
            "old_count": old_count,
            "new_count": new_count
        }

    except Exception as e:
        logger.error(f"Error reloading mentors: {e}")
        raise HTTPException(status_code=500, detail=str(e))
