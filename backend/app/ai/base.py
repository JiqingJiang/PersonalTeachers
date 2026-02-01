"""
AI模型统一接口

定义所有AI模型的抽象基类和工厂方法
"""
from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum


class ModelType(Enum):
    """支持的AI模型类型"""
    GLM = "glm"
    DEEPSEEK = "deepseek"
    MINIMAX = "minimax"
    GEMINI = "gemini"


class LLMProvider(ABC):
    """大语言模型提供者的抽象基类"""

    def __init__(self, api_key: str):
        """
        初始化AI模型提供者

        Args:
            api_key: API密钥
        """
        self.api_key = api_key

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            temperature: 温度参数（0-1，越高越随机）

        Returns:
            生成的文本内容

        Raises:
            APIError: API调用失败
            RateLimitError: 速率限制
            ValidationError: 输入验证失败
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            True if the provider is healthy, False otherwise
        """
        try:
            test_prompt = "你好"
            result = await self.generate(test_prompt, max_tokens=10)
            return len(result) > 0
        except Exception:
            return False


class APIError(Exception):
    """API调用异常"""
    pass


class RateLimitError(APIError):
    """速率限制异常"""
    pass


class ValidationError(APIError):
    """输入验证异常"""
    pass


class QuotaExceededError(APIError):
    """配额用尽异常"""
    pass


# ============================================
# 模型工厂
# ============================================
_providers_cache: dict[ModelType, LLMProvider] = {}


def get_llm_provider(
    model_type: ModelType,
    api_key: Optional[str] = None,
    **kwargs
) -> LLMProvider:
    """
    获取AI模型提供者实例（工厂方法）

    Args:
        model_type: 模型类型
        api_key: API密钥（可选，如果不提供则从缓存获取）
        **kwargs: 其他参数

    Returns:
        LLMProvider实例

    Raises:
        ValueError: 不支持的模型类型
    """
    from .glm import GLMProvider
    from .deepseek import DeepSeekProvider
    from .minimax import MiniMaxProvider
    from .gemini import GeminiProvider

    # 如果提供了api_key，创建新实例
    if api_key is not None:
        if model_type == ModelType.GLM:
            return GLMProvider(api_key)
        elif model_type == ModelType.DEEPSEEK:
            return DeepSeekProvider(api_key, **kwargs)
        elif model_type == ModelType.MINIMAX:
            return MiniMaxProvider(api_key, **kwargs)
        elif model_type == ModelType.GEMINI:
            return GeminiProvider(api_key, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    # 否则尝试从缓存获取
    if model_type in _providers_cache:
        return _providers_cache[model_type]

    raise ValueError(f"No provider found for {model_type}, please provide api_key")


def register_provider(model_type: ModelType, provider: LLMProvider):
    """
    注册AI模型提供者到缓存

    Args:
        model_type: 模型类型
        provider: 提供者实例
    """
    _providers_cache[model_type] = provider


def clear_provider_cache():
    """清空提供者缓存"""
    global _providers_cache
    _providers_cache = {}
