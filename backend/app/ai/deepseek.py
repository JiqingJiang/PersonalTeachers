"""
DeepSeek 集成

使用DeepSeek的API生成文本（兼容OpenAI API）
"""
import asyncio
import os
from typing import Optional
from contextlib import contextmanager
from openai import AsyncOpenAI, APIError as OpenAIError, RateLimitError as OpenAIRateLimit
import httpx
from .base import LLMProvider, APIError, RateLimitError, QuotaExceededError


@contextmanager
def _no_proxy():
    """临时禁用代理的上下文管理器"""
    old_proxies = {}
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                  'ALL_PROXY', 'all_proxy', 'SOCKS_PROXY', 'socks_proxy',
                  'NO_PROXY', 'no_proxy']
    for var in proxy_vars:
        if var in os.environ:
            old_proxies[var] = os.environ[var]
            del os.environ[var]

    try:
        yield
    finally:
        # 恢复代理环境变量
        for var, val in old_proxies.items():
            os.environ[var] = val


class DeepSeekProvider(LLMProvider):
    """
    DeepSeek模型提供者

    API文档: https://platform.deepseek.com/api-docs/
    """

    # DeepSeek支持的模型
    MODELS = {
        "chat": "deepseek-chat",      # 对话模型
        "coder": "deepseek-coder",    # 代码模型
    }

    def __init__(
        self,
        api_key: str,
        model: str = "chat",
        base_url: str = "https://api.deepseek.com"
    ):
        """
        初始化DeepSeek提供者

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称（chat/coder）
            base_url: API基础URL
        """
        super().__init__(api_key)

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {list(self.MODELS.keys())}")

        self.model_name = self.MODELS[model]

        # 在禁用代理的上下文中创建客户端
        with _no_proxy():
            http_client = httpx.AsyncClient(
                timeout=60.0,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                http_client=http_client
            )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        使用DeepSeek生成文本

        Args:
            prompt: 提示词
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            生成的文本内容

        Raises:
            APIError: API调用失败
            RateLimitError: 速率限制
            QuotaExceededError: 配额用尽
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # 提取生成的文本
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise APIError("Empty response from DeepSeek API")

        except OpenAIRateLimit as e:
            raise RateLimitError(f"DeepSeek rate limit: {e}")

        except OpenAIError as e:
            error_msg = str(e)

            # 检查是否是配额用尽
            if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                raise QuotaExceededError(f"DeepSeek quota exceeded: {error_msg}")

            raise APIError(f"DeepSeek API error: {error_msg}")

        except Exception as e:
            raise APIError(f"DeepSeek error: {e}")

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"DeepSeek-{self.model_name}"


# 便捷函数
async def create_deepseek_provider(
    api_key: str,
    model: str = "chat",
    base_url: str = "https://api.deepseek.com"
) -> DeepSeekProvider:
    """
    创建DeepSeek提供者的便捷函数

    Args:
        api_key: DeepSeek API密钥
        model: 模型名称
        base_url: API基础URL

    Returns:
        DeepSeekProvider实例
    """
    return DeepSeekProvider(api_key=api_key, model=model, base_url=base_url)
