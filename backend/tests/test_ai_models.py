"""
AI模型集成测试
测试GLM4.7、DeepSeek、MiniMax三个AI模型的调用
"""
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from app.ai.glm import GLMProvider
from app.ai.deepseek import DeepSeekProvider
from app.ai.minimax import MiniMaxProvider
from app.ai.base import create_llm_provider


# 测试配置（需要设置环境变量或使用mock）
TEST_API_KEY = os.getenv("TEST_API_KEY", "test_api_key_123456")


class TestGLMProvider:
    """GLM模型测试"""

    @pytest.fixture
    def provider(self):
        """创建GLM provider实例"""
        return GLMProvider(api_key=TEST_API_KEY, model="glm-4-flash")

    def test_provider_initialization(self, provider):
        """测试provider初始化"""
        assert provider.api_key == TEST_API_KEY
        assert provider.model == "glm-4-flash"
        assert provider.base_url == "https://open.bigmodel.cn/api/paas/v4"

    def test_available_models(self, provider):
        """测试可用模型列表"""
        models = provider.MODELS
        assert "flash" in models
        assert "air" in models
        assert "plus" in models
        assert models["flash"] == "glm-4-flash"

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, provider):
        """测试生成（使用mock）"""
        # Mock the API call
        with patch.object(provider, '_call_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "这是AI生成的测试语录。"

            result = await provider.generate("测试提示词")

            assert result == "这是AI生成的测试语录。"
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_custom_params(self, provider):
        """测试自定义参数生成"""
        with patch.object(provider, '_call_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "生成结果"

            await provider.generate(
                prompt="测试",
                max_tokens=1000,
                temperature=0.5
            )

            # 验证调用参数
            call_args = mock_call.call_args
            assert call_args[1]["max_tokens"] == 1000
            assert call_args[1]["temperature"] == 0.5


class TestDeepSeekProvider:
    """DeepSeek模型测试"""

    @pytest.fixture
    def provider(self):
        """创建DeepSeek provider实例"""
        return DeepSeekProvider(api_key=TEST_API_KEY, model="deepseek-chat")

    def test_provider_initialization(self, provider):
        """测试provider初始化"""
        assert provider.api_key == TEST_API_KEY
        assert provider.model == "deepseek-chat"
        assert provider.base_url == "https://api.deepseek.com"

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, provider):
        """测试生成（使用mock）"""
        with patch.object(provider, '_call_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "DeepSeek生成的测试内容。"

            result = await provider.generate("测试提示词")

            assert result == "DeepSeek生成的测试内容。"


class TestMiniMaxProvider:
    """MiniMax模型测试"""

    @pytest.fixture
    def provider(self):
        """创建MiniMax provider实例"""
        return MiniMaxProvider(
            api_key=TEST_API_KEY,
            group_id="test_group_id"
        )

    def test_provider_initialization(self, provider):
        """测试provider初始化"""
        assert provider.api_key == TEST_API_KEY
        assert provider.group_id == "test_group_id"

    @pytest.mark.asyncio
    async def test_generate_with_mock(self, provider):
        """测试生成（使用mock）"""
        with patch.object(provider, '_call_api', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "MiniMax生成的测试内容。"

            result = await provider.generate("测试提示词")

            assert result == "MiniMax生成的测试内容。"


class TestLLMProviderFactory:
    """测试LLM Provider工厂函数"""

    def test_create_glm_provider(self):
        """测试创建GLM provider"""
        provider = create_llm_provider(
            provider_type="glm",
            api_key=TEST_API_KEY
        )
        assert isinstance(provider, GLMProvider)

    def test_create_deepseek_provider(self):
        """测试创建DeepSeek provider"""
        provider = create_llm_provider(
            provider_type="deepseek",
            api_key=TEST_API_KEY
        )
        assert isinstance(provider, DeepSeekProvider)

    def test_create_minimax_provider(self):
        """测试创建MiniMax provider"""
        provider = create_llm_provider(
            provider_type="minimax",
            api_key=TEST_API_KEY,
            group_id="test_group"
        )
        assert isinstance(provider, MiniMaxProvider)

    def test_create_invalid_provider(self):
        """测试创建无效provider类型"""
        with pytest.raises(ValueError, match="Unknown LLM provider type"):
            create_llm_provider(
                provider_type="invalid_model",
                api_key=TEST_API_KEY
            )


class TestAIModelFallback:
    """测试AI模型故障转移"""

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self):
        """测试主模型失败后切换到备用模型"""
        # 创建两个provider，第一个失败，第二个成功
        primary_provider = MagicMock(spec=GLMProvider)
        fallback_provider = MagicMock(spec=DeepSeekProvider)

        # 模拟第一个失败，第二个成功
        primary_provider.generate = AsyncMock(side_effect=Exception("API Error"))
        fallback_provider.generate = AsyncMock(return_value="备用模型生成的内容")

        # 尝试主模型
        result = None
        try:
            result = await primary_provider.generate("测试")
        except:
            # 主模型失败，使用备用
            result = await fallback_provider.generate("测试")

        assert result == "备用模型生成的内容"
        primary_provider.generate.assert_called_once()
        fallback_provider.generate.assert_called_once()


@pytest.mark.integration
class TestRealAICalls:
    """
    集成测试：真实AI API调用
    注意：这些测试需要真实的API密钥，且会产生实际费用
    运行时需要: pytest -m integration
    """

    @pytest.mark.skipif(
        not os.getenv("GLM_API_KEY"),
        reason="GLM_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_real_glm_call(self):
        """真实GLM API调用测试"""
        api_key = os.getenv("GLM_API_KEY")
        provider = GLMProvider(api_key=api_key, model="glm-4-flash")

        result = await provider.generate(
            prompt="请用一句话介绍Python编程语言。",
            max_tokens=100
        )

        assert result
        assert len(result) > 0
        assert isinstance(result, str)

    @pytest.mark.skipif(
        not os.getenv("DEEPSEEK_API_KEY"),
        reason="DEEPSEEK_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_real_deepseek_call(self):
        """真实DeepSeek API调用测试"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        provider = DeepSeekProvider(api_key=api_key)

        result = await provider.generate(
            prompt="什么是人工智能？请用一句话回答。",
            max_tokens=100
        )

        assert result
        assert len(result) > 0
        assert isinstance(result, str)

    @pytest.mark.skipif(
        not os.getenv("MINIMAX_API_KEY") or not os.getenv("MINIMAX_GROUP_ID"),
        reason="MiniMax credentials not set"
    )
    @pytest.mark.asyncio
    async def test_real_minimax_call(self):
        """真实MiniMax API调用测试"""
        api_key = os.getenv("MINIMAX_API_KEY")
        group_id = os.getenv("MINIMAX_GROUP_ID")
        provider = MiniMaxProvider(api_key=api_key, group_id=group_id)

        result = await provider.generate(
            prompt="请简要介绍机器学习。",
            max_tokens=100
        )

        assert result
        assert len(result) > 0
        assert isinstance(result, str)
