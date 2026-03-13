"""
AI模型集成模块

提供统一的接口访问多个AI模型（GLM4.7/DeepSeek/MiniMax/Gemini）
"""
from .base import (
    LLMProvider,
    ModelType,
    APIError,
    RateLimitError,
    ValidationError,
    QuotaExceededError,
    get_llm_provider,
    register_provider,
    clear_provider_cache
)

from .glm import GLMProvider, create_glm_provider
from .deepseek import DeepSeekProvider, create_deepseek_provider
from .minimax import MiniMaxProvider, create_minimax_provider
from .gemini import GeminiProvider, create_gemini_provider

__all__ = [
    # 基础接口
    "LLMProvider",
    "ModelType",
    "APIError",
    "RateLimitError",
    "ValidationError",
    "QuotaExceededError",
    "get_llm_provider",
    "register_provider",
    "clear_provider_cache",

    # 具体实现
    "GLMProvider",
    "create_glm_provider",
    "DeepSeekProvider",
    "create_deepseek_provider",
    "MiniMaxProvider",
    "create_minimax_provider",
    "GeminiProvider",
    "create_gemini_provider",
]
