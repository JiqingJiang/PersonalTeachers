"""
MiniMax 集成

使用MiniMax的API生成文本
"""
import asyncio
from typing import Optional
import httpx
from .base import LLMProvider, APIError, RateLimitError, QuotaExceededError


class MiniMaxProvider(LLMProvider):
    """
    MiniMax模型提供者

    API文档: https://www.minimaxi.com/document/guides/chat/gpt_by_call
    """

    # MiniMax支持的模型
    MODELS = {
        "abab6": "abab6-chat",       # abab6系列
        "abab5": "abab5.5-chat",     # abab5.5系列
    }

    # API端点
    API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

    def __init__(
        self,
        api_key: str,
        group_id: str,
        model: str = "abab6"
    ):
        """
        初始化MiniMax提供者

        Args:
            api_key: MiniMax API密钥
            group_id: MiniMax Group ID
            model: 模型名称（abab6/abab5）
        """
        super().__init__(api_key)

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {list(self.MODELS.keys())}")

        self.model_name = self.MODELS[model]
        self.group_id = group_id
        self.api_url = self.API_URL

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        使用MiniMax生成文本

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
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "tokens_to_generate": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )

                # 检查HTTP状态码
                if response.status_code == 429:
                    raise RateLimitError("MiniMax rate limit exceeded")

                elif response.status_code == 402:
                    raise QuotaExceededError("MiniMax quota exceeded")

                elif response.status_code != 200:
                    raise APIError(f"MiniMax API error (HTTP {response.status_code}): {response.text}")

                # 解析响应
                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["text"]
                else:
                    raise APIError(f"Unexpected MiniMax response format: {data}")

        except httpx.TimeoutException:
            raise APIError("MiniMax API timeout")

        except httpx.NetworkError as e:
            raise APIError(f"MiniMax network error: {e}")

        except (RateLimitError, QuotaExceededError, APIError):
            raise

        except Exception as e:
            raise APIError(f"MiniMax error: {e}")

    def get_model_name(self) -> str:
        """获取模型名称"""
        return f"MiniMax-{self.model_name}"


# 便捷函数
async def create_minimax_provider(
    api_key: str,
    group_id: str,
    model: str = "abab6"
) -> MiniMaxProvider:
    """
    创建MiniMax提供者的便捷函数

    Args:
        api_key: MiniMax API密钥
        group_id: MiniMax Group ID
        model: 模型名称

    Returns:
        MiniMaxProvider实例
    """
    return MiniMaxProvider(api_key=api_key, group_id=group_id, model=model)
