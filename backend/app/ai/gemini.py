"""
Google Gemini 集成

使用 Google AI Studio 的 Gemini 模型生成文本
"""
import asyncio
from typing import Optional
import google.generativeai as genai
from .base import LLMProvider, APIError, RateLimitError, QuotaExceededError


class GeminiProvider(LLMProvider):
    """
    Gemini 模型提供者

    API文档: https://ai.google.dev/docs
    获取API Key: https://makersuite.google.com/app/apikey
    """

    # 推荐的模型列表（按成本排序）
    MODELS = {
        "flash": "gemini-2.0-flash-exp",      # 最快、最便宜
        "pro": "gemini-1.5-pro",              # 平衡
        "flash-8b": "gemini-1.5-flash-8b",    # 轻量级
        "latest": "gemini-2.0-flash-exp"      # 默认最新
    }

    def __init__(
        self,
        api_key: str,
        model: str = "flash"
    ):
        """
        初始化 Gemini 提供者

        Args:
            api_key: Google AI API 密钥
            model: 模型名称（flash/pro/flash-8b/latest）
        """
        super().__init__(api_key)

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {list(self.MODELS.keys())}")

        self.model_name = self.MODELS[model]
        genai.configure(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        使用 Gemini 生成文本

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
            # 创建模型实例
            model = genai.GenerativeModel(self.model_name)

            # 在线程池中执行同步调用
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                )
            )

            # 提取生成的文本
            if response and response.text:
                return response.text
            else:
                raise APIError("Empty response from Gemini API")

        except Exception as e:
            error_msg = str(e)

            # 处理特定错误类型
            if "quota" in error_msg.lower() or "billing" in error_msg.lower():
                raise QuotaExceededError(f"Gemini quota exceeded: {error_msg}")

            elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                raise RateLimitError(f"Gemini rate limit: {error_msg}")

            elif "blocked" in error_msg.lower():
                raise APIError(f"Gemini content blocked: {error_msg}")

            else:
                raise APIError(f"Gemini API error: {error_msg}")

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"Gemini-{self.model_name}"

    async def count_tokens(self, text: str) -> int:
        """
        估算文本的token数（粗略估算）

        Args:
            text: 输入文本

        Returns:
            估算的token数
        """
        # 中文：约1.5字符/token，英文：约4字符/token
        # 这里使用粗略估算：中文按1.5，英文按4
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars

        return int(chinese_chars / 1.5 + other_chars / 4)


# 便捷函数
async def create_gemini_provider(
    api_key: str,
    model: str = "flash"
) -> GeminiProvider:
    """
    创建 Gemini 提供者的便捷函数

    Args:
        api_key: Google AI API 密钥
        model: 模型名称

    Returns:
        GeminiProvider 实例
    """
    return GeminiProvider(api_key=api_key, model=model)
