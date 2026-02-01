"""
统计信息API端点
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from datetime import datetime, timedelta
from typing import Dict

from app.models.database import QuoteDB, StatsResponse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from app.core import get_mentor_pool
from app.core.weight_scheduler import get_keyword_scheduler


router = APIRouter(prefix="/api", tags=["统计"])


@router.get("/system-info")
async def get_system_info() -> Dict:
    """
    获取系统基础信息

    包括导师总数、关键词总数等元数据
    """
    try:
        # 获取导师池信息
        mentor_pool = get_mentor_pool()
        all_mentors = mentor_pool.get_all_mentors()

        # 统计各类别导师数量
        from app.models.database import MentorCategory
        category_counts = {}
        for category in MentorCategory:
            count = len(mentor_pool.get_mentors_by_category(category))
            category_counts[category.value] = count

        # 获取关键词信息
        keyword_scheduler = get_keyword_scheduler()
        keywords = keyword_scheduler.get_all_keywords()

        return {
            "total_mentors": len(all_mentors),
            "total_keywords": len(keywords),
            "mentor_categories": category_counts,
            "keywords": keywords
        }

    except Exception as e:
        logger.error(f"Error fetching system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """
    获取统计信息

    包括语录总数、各维度分布、AI模型使用情况等
    """
    try:
        db_path = Path(__file__).parent.parent.parent / "storage" / "quotes.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 总数
            total_quotes = session.query(func.count(QuoteDB.id)).scalar() or 0

            # 本周
            week_ago = datetime.utcnow() - timedelta(days=7)
            quotes_this_week = session.query(func.count(QuoteDB.id)).filter(
                QuoteDB.created_at >= week_ago
            ).scalar() or 0

            # 本月
            month_ago = datetime.utcnow() - timedelta(days=30)
            quotes_this_month = session.query(func.count(QuoteDB.id)).filter(
                QuoteDB.created_at >= month_ago
            ).scalar() or 0

            # 按关键词统计
            keyword_counts = {}
            try:
                for result in session.query(
                    QuoteDB.keyword,
                    func.count(QuoteDB.id)
                ).group_by(QuoteDB.keyword).all():
                    keyword_counts[result[0]] = result[1]
            except:
                pass

            # 按导师类别统计
            category_counts = {}
            try:
                for result in session.query(
                    QuoteDB.mentor_category,
                    func.count(QuoteDB.id)
                ).group_by(QuoteDB.mentor_category).all():
                    category_counts[result[0]] = result[1]
            except:
                pass

            # 按AI模型统计
            model_counts = {}
            try:
                for result in session.query(
                    QuoteDB.ai_model,
                    func.count(QuoteDB.id)
                ).group_by(QuoteDB.ai_model).all():
                    model_counts[result[0]] = result[1]
            except:
                pass

            return StatsResponse(
                total_quotes=total_quotes,
                quotes_this_week=quotes_this_week,
                quotes_this_month=quotes_this_month,
                by_keyword=keyword_counts,
                by_mentor_category=category_counts,
                ai_model_usage=model_counts
            )

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        # 返回空统计而不是抛出异常（允许首次运行）
        return StatsResponse(
            total_quotes=0,
            quotes_this_week=0,
            quotes_this_month=0,
            by_keyword={},
            by_mentor_category={},
            ai_model_usage={}
        )
