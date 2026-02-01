#!/usr/bin/env python3
"""
快速修改推送时间工具
将推送时间设置为当前时间+N分钟
"""
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def set_delivery_time(minutes_ahead: int = 2):
    """
    设置推送时间为当前时间+N分钟

    Args:
        minutes_ahead: 提前多少分钟（默认2）
    """
    config_path = PROJECT_ROOT / "data" / "config.yaml"

    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    original_time = config.get('delivery', {}).get('time', '08:00')

    # 计算新时间
    now = datetime.now()
    target_time = now + timedelta(minutes=minutes_ahead, seconds=10)  # 多加10秒确保触发
    new_time = target_time.strftime("%H:%M")

    # 修改配置
    config['delivery']['time'] = new_time

    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"✅ 推送时间已修改")
    print(f"   原时间: {original_time}")
    print(f"   新时间: {new_time}")
    print(f"   当前: {now.strftime('%H:%M:%S')}")
    print(f"   将在约 {minutes_ahead} 分钟后触发")
    print()
    print("🚀 现在请重启服务:")
    print("   cd backend")
    print("   python run.py")
    print()
    print("⏳ 服务启动后会看到:")
    print(f"   ⏰ Scheduler started (daily at {new_time})")
    print()
    print("📧 等待触发后，会自动生成并发送邮件")
    print()
    print("💡 测试完成后，请恢复原时间:")
    print(f"   # 将 config.yaml 中的 time 改回 {original_time}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='设置定时推送时间')
    parser.add_argument('--minutes', type=int, default=2,
                       help='提前多少分钟 (默认: 2)')

    args = parser.parse_args()

    print("=" * 60)
    print("⏰ 定时推送时间设置工具")
    print("=" * 60)
    print()

    try:
        set_delivery_time(args.minutes)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
