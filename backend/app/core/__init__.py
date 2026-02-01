"""
核心业务逻辑模块

包含导师池管理、权重调度、语录生成引擎等核心功能
"""
from .mentor_pool import MentorPool, get_mentor_pool, MentorData
from .weight_scheduler import KeywordScheduler, get_keyword_scheduler
from .quote_engine import QuoteEngine, get_quote_engine
from .future_self import FutureSelfGenerator, get_future_self_generator

__all__ = [
    # 导师池
    "MentorPool",
    "get_mentor_pool",
    "MentorData",

    # 权重调度
    "KeywordScheduler",
    "get_keyword_scheduler",

    # 语录生成
    "QuoteEngine",
    "get_quote_engine",

    # 未来自己
    "FutureSelfGenerator",
    "get_future_self_generator",
]
