#!/usr/bin/env python3
"""
手动测试定时发送的快速指南

方式A：修改配置重启服务
方式B：查看调度器状态
"""
import sys
from pathlib import Path
import yaml
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def show_manual_test_guide():
    """显示手动测试指南"""
    print("⏰ 定时发送功能 - 手动测试指南")
    print("=" * 70)

    # 计算建议时间
    now = datetime.now()
    test_time = (now + timedelta(minutes=2)).strftime("%H:%M")

    print("\n【方式A】修改推送时间后重启（推荐）")
    print("-" * 70)
    print("1. 编辑配置文件:")
    print("   vim backend/data/config.yaml")
    print()
    print("2. 修改推送时间为一分钟后:")
    print(f"   delivery:")
    print(f"     time: \"{test_time}\"  # 改为 {test_time}")
    print()
    print("3. 重启服务:")
    print("   cd backend")
    print("   python run.py")
    print()
    print("4. 观察日志，等待邮件发送")
    print("   会看到类似这样的日志:")
    print("   ⏰ Scheduler started (daily at {test_time})")
    print("   📧 开始生成语录...")
    print("   ✅ 邮件发送成功")
    print()
    print("5. 恢复原配置:")
    print("   # 将 time 改回 08:00")
    print()

    print("\n【方式B】查看当前调度状态")
    print("-" * 70)
    print("查看服务日志:")
    print("  cd backend")
    print("  python run.py")
    print()
    print("启动后会显示:")
    print("  ⏰ Scheduler started (daily at 08:00)")
    print()
    print("这表示调度器已正常运行")
    print("会在每天 08:00 自动发送")
    print()

    print("\n【方式C】验证配置")
    print("-" * 70)

    config_path = PROJECT_ROOT / "data" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    delivery = config.get('delivery', {})
    user = config.get('user', {})

    print(f"当前配置:")
    print(f"  推送时间: {delivery.get('time', '未设置')}")
    print(f"  启用状态: {delivery.get('enabled', False)}")
    print(f"  接收邮箱: {user.get('email', '未设置')}")
    print(f"  时区: {delivery.get('timezone', '未设置')}")
    print()

    if not delivery.get('enabled'):
        print("⚠️  定时推送未启用！")
        print("   在 config.yaml 中设置:")
        print("   delivery:")
        print("     enabled: true")
    else:
        print("✅ 定时推送已启用")
        print(f"   将在每天 {delivery.get('time')} 发送")

    print("\n" + "=" * 70)
    print("\n💡 提示:")
    print("  • 修改配置后需重启服务才能生效")
    print("  • 建议测试时设置为2-3分钟后")
    print("  • 确保已配置好AI密钥和邮箱SMTP")
    print()


if __name__ == "__main__":
    show_manual_test_guide()
