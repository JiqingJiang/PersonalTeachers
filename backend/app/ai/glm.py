"""
GLM4.7 (智谱AI) 集成

使用智谱AI的GLM-4系列模型生成文本
"""
import asyncio
import os
from typing import Optional
from zhipuai import ZhipuAI
from .base import LLMProvider, APIError, RateLimitError, QuotaExceededError


class GLMProvider(LLMProvider):
    """
    GLM-4模型提供者

    API文档: https://open.bigmodel.cn/dev/api
    """

    # 推荐的模型列表（按成本排序）
    MODELS = {
        "flash": "glm-4-flash",      # 最快、最便宜
        "air": "glm-4-air",          # 平衡
        "plus": "glm-4-plus",        # 高质量
        "latest": "glm-4"            # 默认最新
    }

    def __init__(
        self,
        api_key: str,
        model: str = "flash"
    ):
        """
        初始化GLM提供者

        Args:
            api_key: 智谱AI API密钥
            model: 模型名称（flash/air/plus/latest）
        """
        super().__init__(api_key)

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {list(self.MODELS.keys())}")

        self.model_name = self.MODELS[model]

        # 临时清除代理环境变量，避免SOCKS代理错误
        old_proxies = {}
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
                      'ALL_PROXY', 'all_proxy', 'SOCKS_PROXY', 'socks_proxy']
        for var in proxy_vars:
            if var in os.environ:
                old_proxies[var] = os.environ[var]
                del os.environ[var]

        try:
            self.client = ZhipuAI(api_key=api_key)
        finally:
            # 恢复代理环境变量
            for var, val in old_proxies.items():
                os.environ[var] = val

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        使用GLM生成文本

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
            # 在线程池中执行同步调用
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
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
                raise APIError("Empty response from GLM API")

        except Exception as e:
            error_msg = str(e)

            # 处理特定错误类型
            if "129" in error_msg or "130" in error_msg:
                # 129: concurrent limit exceeded
                # 130: rate limit exceeded
                raise RateLimitError(f"GLM rate limit: {error_msg}")

            elif "110" in error_msg or "111" in error_msg:
                # 110: Token quota is not enough
                # 111: Quota exhausted
                raise QuotaExceededError(f"GLM quota exceeded: {error_msg}")

            elif "127" in error_msg:
                # 127: Invalid request
                raise APIError(f"GLM validation error: {error_msg}")

            else:
                raise APIError(f"GLM API error: {error_msg}")

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"GLM-{self.model_name}"

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
async def create_glm_provider(
    api_key: str,
    model: str = "flash"
) -> GLMProvider:
    """
    创建GLM提供者的便捷函数

    Args:
        api_key: 智谱AI API密钥
        model: 模型名称

    Returns:
        GLMProvider实例
    """
    return GLMProvider(api_key=api_key, model=model)
