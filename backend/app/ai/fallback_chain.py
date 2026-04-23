"""多模型降级链

按优先级依次尝试多个 AI 模型，直到成功或全部失败。
"""

import asyncio
from loguru import logger

from app.ai.base import LLMProvider, RateLimitError, QuotaExceededError, AIError
from app.ai.openai_adapter import OpenAICompatibleProvider


class FallbackChain:
    """多模型降级链"""

    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self._providers: dict[str, LLMProvider] = {}

    def get_or_create_provider(self, base_url: str, api_key: str, model_id: str) -> LLMProvider:
        """缓存 Provider 实例，避免重复创建"""
        cache_key = f"{base_url}|{model_id}"
        if cache_key not in self._providers:
            self._providers[cache_key] = OpenAICompatibleProvider(
                base_url=base_url, api_key=api_key, model_id=model_id
            )
        return self._providers[cache_key]

    def clear_cache(self):
        """清除缓存的 Provider 实例（配置变更时调用）"""
        self._providers.clear()

    async def generate(
        self,
        prompt: str,
        model_configs: list[dict],
        max_tokens: int = 300,
        temperature: float = 0.7,
    ) -> tuple[str, str]:
        """
        按优先级尝试多个模型生成文本。

        Args:
            prompt: 提示词
            model_configs: 模型配置列表（按优先级排序），每项包含 base_url, api_key, model_id, name
            max_tokens: 最大 token 数
            temperature: 温度

        Returns:
            (生成文本, 使用的模型名称)

        Raises:
            AIError: 所有模型都失败
        """
        last_error = None

        for config in model_configs:
            name = config["name"]
            api_key = config.get("api_key", "")
            if not api_key:
                continue

            provider = self.get_or_create_provider(
                base_url=config["base_url"],
                api_key=api_key,
                model_id=config["model_id"],
            )

            for attempt in range(self.max_retries):
                try:
                    result = await provider.generate(prompt, max_tokens, temperature)
                    logger.info(f"模型 {name} 生成成功 (尝试 {attempt + 1})")
                    return result, name
                except (RateLimitError, QuotaExceededError) as e:
                    logger.warning(f"模型 {name} 限流/配额不足: {e}，切换下一个模型")
                    last_error = e
                    break  # 切换模型，不再重试
                except AIError as e:
                    logger.warning(f"模型 {name} 失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                    last_error = e

        raise AIError(f"所有模型均失败: {last_error}")
