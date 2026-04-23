"""AI 模型抽象接口和异常体系"""

from abc import ABC, abstractmethod


class AIError(Exception):
    """AI 调用基础异常"""
    pass


class RateLimitError(AIError):
    """速率限制"""
    pass


class QuotaExceededError(AIError):
    """配额耗尽"""
    pass


class InvalidRequestError(AIError):
    """无效请求"""
    pass


class LLMProvider(ABC):
    """大模型 Provider 抽象基类"""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
