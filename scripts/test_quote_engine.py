#!/usr/bin/env python3
"""
语录生成测试脚本

测试语录生成引擎的核心功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from dotenv import load_dotenv
from app.core import get_quote_engine, get_mentor_pool, get_keyword_scheduler


async def test_quote_generation():
    """测试语录生成"""
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                           ║
║   📝 PersonalTeachers 语录生成测试                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════╝
    """)

    # 加载环境变量
    env_path = PROJECT_ROOT / "backend" / ".env"
    load_dotenv(env_path)

    # 测试1: 导师池加载
    print("\n" + "=" * 50)
    print("🧪 测试1: 导师池加载")
    print("=" * 50)

    try:
        mentor_pool = get_mentor_pool()
        mentors = mentor_pool.get_all_mentors()
        print(f"✅ 导师池加载成功！共有 {len(mentors)} 位导师")

        # 按类别统计
        from app.models.database import MentorCategory
        for category in MentorCategory:
            count = len(mentor_pool.get_mentors_by_category(category))
            print(f"   - {category.value}: {count}位")

    except Exception as e:
        print(f"❌ 导师池加载失败: {e}")
        return

    # 测试2: 关键词加载
    print("\n" + "=" * 50)
    print("🧪 测试2: 关键词加载")
    print("=" * 50)

    try:
        scheduler = get_keyword_scheduler()
        keywords = scheduler.get_all_keywords()
        print(f"✅ 关键词加载成功！共有 {len(keywords)} 个关键词")

        # 按象限统计
        for quadrant in range(1, 5):
            count = len(scheduler.get_keywords_by_quadrant(quadrant))
            print(f"   - 第{quadrant}象限: {count}个")

    except Exception as e:
        print(f"❌ 关键词加载失败: {e}")
        return

    # 测试3: 关键词选择
    print("\n" + "=" * 50)
    print("🧪 测试3: 关键词权重选择")
    print("=" * 50)

    try:
        # 测试权重
        test_weights = {
            "健康": 2.0,
            "选择": 2.5,
            "焦虑": 2.0,
            "金钱": 0.5
        }

        selected = scheduler.select_keywords(
            count=5,
            user_weights=test_weights,
            ensure_diversity=True
        )

        print(f"✅ 关键词选择成功！")
        print(f"   权重配置: {test_weights}")
        print(f"   选中的关键词: {selected}")

        # 统计象限分布
        distribution = scheduler.get_quadrant_distribution(selected)
        print(f"   象限分布: {distribution}")

    except Exception as e:
        print(f"❌ 关键词选择失败: {e}")
        return

    # 测试4: 导师匹配
    print("\n" + "=" * 50)
    print("🧪 测试4: 导师匹配")
    print("=" * 50)

    try:
        test_keyword = "健康"
        mentors = mentor_pool.get_mentors_by_keyword(test_keyword)
        print(f"✅ 关键词【{test_keyword}】的匹配导师:")
        for mentor in mentors[:5]:
            print(f"   - {mentor.name} ({mentor.category.value})")

    except Exception as e:
        print(f"❌ 导师匹配失败: {e}")
        return

    # 测试5: 语录生成（需要API密钥）
    print("\n" + "=" * 50)
    print("🧪 测试5: AI语录生成")
    print("=" * 50)

    try:
        import os
        api_key = os.getenv("ZHIPUAI_API_KEY")

        if not api_key or api_key == "your-key-here":
            print("⚠️  跳过：未配置API密钥")
            print("   请在 backend/.env 中配置 ZHIPUAI_API_KEY")
            print("   然后重新运行此测试")
            return

        print("🔄 正在生成语录（这可能需要几秒钟）...")

        engine = get_quote_engine()

        # 生成1条语录作为测试
        quotes = await engine.generate_quotes(count=1)

        if quotes:
            quote = quotes[0]
            print(f"\n✅ 语录生成成功！")
            print(f"\n📖 导师: {quote['mentor_name']} ({quote['mentor_category']})")
            print(f"🎯 主题: 【{quote['keyword']}】")
            print(f"\n💬 语录内容:")
            print(f"   {quote['content']}")
        else:
            print("❌ 语录生成失败：未返回内容")

    except Exception as e:
        print(f"❌ 语录生成失败: {e}")
        import traceback
        traceback.print_exc()

    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    print("✅ 核心功能测试完成！")
    print("\n💡 下一步:")
    print("   1. 配置API密钥 (backend/.env)")
    print("   2. 运行完整系统: python backend/run.py")


if __name__ == "__main__":
    asyncio.run(test_quote_generation())
