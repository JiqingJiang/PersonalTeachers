"""统一 OpenAI 兼容适配器

一个适配器覆盖所有 OpenAI 兼容的 API：
- DeepSeek: base_url=https://api.deepseek.com
- 智谱GLM: base_url=https://open.bigmodel.cn/api/paas/v4
- 任何 OpenAI 兼容接口（本地 Ollama 等）
"""

from openai import AsyncOpenAI
from loguru import logger

from app.ai.base import LLMProvider, RateLimitError, QuotaExceededError, AIError


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, model_id: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model_id = model_id

    async def generate(self, prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if content is None:
                raise AIError("模型返回空内容")
            return content.strip()
        except Exception as e:
            error_msg = str(e).lower()
            if "rate_limit" in error_msg or "429" in error_msg:
                raise RateLimitError(f"速率限制: {e}")
            if "quota" in error_msg or "insufficient" in error_msg or "402" in error_msg:
                raise QuotaExceededError(f"配额不足: {e}")
            if "invalid" in error_msg or "400" in error_msg:
                raise AIError(f"无效请求: {e}")
            raise AIError(f"生成失败: {e}")

    def get_model_name(self) -> str:
        return self.model_id
