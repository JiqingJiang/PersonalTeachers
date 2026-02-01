#!/usr/bin/env python3
"""
测试AI模型生成功能
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv(PROJECT_ROOT / ".env")


async def test_ai_models():
    """测试所有配置的AI模型"""
    print("🤖 测试AI模型生成功能")
    print("=" * 60)

    from app.ai import get_llm_provider, ModelType

    # 测试配置
    test_prompt = "请用一句话介绍什么是人工智能。"

    models_to_test = []

    # 检查哪些模型已配置
    if os.getenv("ZHIPUAI_API_KEY") and os.getenv("ZHIPUAI_API_KEY") != "your-key-here":
        models_to_test.append(("GLM4.7", ModelType.GLM, os.getenv("ZHIPUAI_API_KEY")))

    if os.getenv("DEEPSEEK_API_KEY") and os.getenv("DEEPSEEK_API_KEY") != "sk-your-key-here":
        models_to_test.append(("DeepSeek", ModelType.DEEPSEEK, os.getenv("DEEPSEEK_API_KEY")))

    if len(models_to_test) == 0:
        print("❌ 没有配置任何AI模型API密钥")
        print("\n请在 .env 文件中配置至少一个API密钥:")
        print("  • ZHIPUAI_API_KEY (GLM4.7)")
        print("  • DEEPSEEK_API_KEY (DeepSeek)")
        return

    print(f"发现 {len(models_to_test)} 个已配置的AI模型\n")

    # 测试每个模型
    for name, model_type, api_key in models_to_test:
        print(f"🔄 测试 {name}...")
        try:
            provider = get_llm_provider(model_type, api_key=api_key)
            result = await provider.generate(
                prompt=test_prompt,
                max_tokens=100,
                temperature=0.7
            )
            print(f"✅ {name} 生成成功")
            print(f"   回答: {result[:100]}...")
            print()
        except Exception as e:
            print(f"❌ {name} 失败: {e}")
            print()

    print("=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    asyncio.run(test_ai_models())
