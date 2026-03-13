"""
API路由模块

包含所有API端点
"""
from fastapi import APIRouter

# 创建主路由
api_router = APIRouter()

# 导入各个子路由
from . import quotes, mentors, config, email, stats, keywords

# 注册子路由
api_router.include_router(quotes.router)
api_router.include_router(mentors.router)
api_router.include_router(config.router)
api_router.include_router(email.router)
api_router.include_router(stats.router)
api_router.include_router(keywords.router)

__all__ = ["api_router"]
