"""
语录相关API端点

提供语录生成、历史查询等功能
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.database import (
    QuoteResponse,
    QuoteGenerateRequest,
    StatsResponse
)
from app.core import get_quote_engine


router = APIRouter(prefix="/api/quotes", tags=["语录"])


@router.post("/generate", response_model=List[QuoteResponse])
async def generate_quotes(request: QuoteGenerateRequest):
    """
    生成语录

    根据配置的权重和偏好生成指定数量的语录
    """
    try:
        logger.info(f"Generating {request.count} quotes...")

        engine = get_quote_engine()

        quotes_data = await engine.generate_quotes(
            count=request.count,
            keyword_weights=request.keyword_weights,
            mentor_preferences=request.mentor_preferences
        )

        if not quotes_data:
            raise HTTPException(status_code=500, detail="Failed to generate quotes")

        # 转换为响应模型
        quotes = [
            QuoteResponse(
                id=i,
                mentor_name=q['mentor_name'],
                mentor_category=q['mentor_category'],
                mentor_age=q.get('mentor_age'),
                keyword=q['keyword'],
                content=q['content'],
                ai_model=q.get('ai_model', 'auto'),
                created_at=q.get('created_at', datetime.utcnow())
            )
            for i, q in enumerate(quotes_data)
        ]

        return quotes

    except Exception as e:
        logger.error(f"Error generating quotes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_quote_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    sort_by: str = Query("date_desc", description="排序方式"),
    keyword: Optional[str] = Query(None, description="按关键词筛选"),
    mentor: Optional[str] = Query(None, description="按导师名称筛选"),
    date: Optional[str] = Query(None, description="按日期筛选(YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="搜索内容")
):
    """
    获取历史语录

    支持分页、筛选、搜索等功能
    """
    try:
        from app.models.database import QuoteDB
        from sqlalchemy import create_engine, or_, and_
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path
        from pydantic import BaseModel

        class HistoryResponse(BaseModel):
            quotes: List[QuoteResponse]
            total: int

        # 连接数据库
        db_path = Path(__file__).parent.parent.parent / "storage" / "quotes.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 构建查询
            query = session.query(QuoteDB)

            # 关键词筛选
            if keyword:
                query = query.filter(QuoteDB.keyword == keyword)

            # 导师名称筛选
            if mentor:
                query = query.filter(QuoteDB.mentor_name == mentor)

            # 日期筛选
            if date:
                try:
                    filter_date = datetime.strptime(date, "%Y-%m-%d").date()
                    next_day = filter_date + timedelta(days=1)
                    query = query.filter(
                        QuoteDB.created_at >= datetime.combine(filter_date, datetime.min.time()),
                        QuoteDB.created_at < datetime.combine(next_day, datetime.min.time())
                    )
                except ValueError:
                    pass

            # 搜索功能（内容、导师名称、关键词）
            if search:
                query = query.filter(
                    or_(
                        QuoteDB.content.like(f"%{search}%"),
                        QuoteDB.mentor_name.like(f"%{search}%"),
                        QuoteDB.keyword.like(f"%{search}%")
                    )
                )

            # 获取总数
            total = query.count()

            # 排序
            if sort_by == "date_desc":
                query = query.order_by(QuoteDB.created_at.desc())
            elif sort_by == "date_asc":
                query = query.order_by(QuoteDB.created_at.asc())

            # 分页
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            quotes_db = query.all()

            # 转换为响应模型
            quotes = [
                QuoteResponse(
                    id=q.id,
                    mentor_name=q.mentor_name,
                    mentor_category=q.mentor_category,
                    mentor_age=q.mentor_age,
                    keyword=q.keyword,
                    content=q.content,
                    ai_model=q.ai_model,
                    created_at=q.created_at,
                    quality_score=q.quality_score or 0.0
                )
                for q in quotes_db
            ]

            return HistoryResponse(quotes=quotes, total=total)

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error fetching quote history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote_by_id(quote_id: int):
    """
    获取单条语录详情
    """
    try:
        from app.models.database import QuoteDB
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path

        db_path = Path(__file__).parent.parent.parent / "storage" / "quotes.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            quote_db = session.query(QuoteDB).filter(QuoteDB.id == quote_id).first()

            if not quote_db:
                raise HTTPException(status_code=404, detail="Quote not found")

            return QuoteResponse(
                id=quote_db.id,
                mentor_name=quote_db.mentor_name,
                mentor_category=quote_db.mentor_category,
                mentor_age=quote_db.mentor_age,
                keyword=quote_db.keyword,
                content=quote_db.content,
                ai_model=quote_db.ai_model,
                created_at=quote_db.created_at,
                quality_score=quote_db.quality_score or 0.0
            )

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_statistics():
    """
    获取统计信息

    包括语录总数、各维度分布、AI模型使用情况等
    """
    try:
        from app.models.database import QuoteDB
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path
        from datetime import timedelta

        db_path = Path(__file__).parent.parent.parent / "storage" / "quotes.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 总数
            total_quotes = session.query(func.count(QuoteDB.id)).scalar()

            # 本周
            week_ago = datetime.utcnow() - timedelta(days=7)
            quotes_this_week = session.query(func.count(QuoteDB.id)).filter(
                QuoteDB.created_at >= week_ago
            ).scalar()

            # 本月
            month_ago = datetime.utcnow() - timedelta(days=30)
            quotes_this_month = session.query(func.count(QuoteDB.id)).filter(
                QuoteDB.created_at >= month_ago
            ).scalar()

            # 按关键词统计
            keyword_counts = {}
            for result in session.query(
                QuoteDB.keyword,
                func.count(QuoteDB.id)
            ).group_by(QuoteDB.keyword).all():
                keyword_counts[result[0]] = result[1]

            # 按导师类别统计
            category_counts = {}
            for result in session.query(
                QuoteDB.mentor_category,
                func.count(QuoteDB.id)
            ).group_by(QuoteDB.mentor_category).all():
                category_counts[result[0]] = result[1]

            # 按AI模型统计
            model_counts = {}
            for result in session.query(
                QuoteDB.ai_model,
                func.count(QuoteDB.id)
            ).group_by(QuoteDB.ai_model).all():
                model_counts[result[0]] = result[1]

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
        raise HTTPException(status_code=500, detail=str(e))
