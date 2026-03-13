#!/usr/bin/env python3
"""
测试定时发送功能

修改临时配置，将推送时间设置为当前时间+1分钟
然后等待定时任务触发
"""
import sys
import asyncio
import yaml
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")


def get_next_minute():
    """获取下一分钟的时间（HH:MM格式）"""
    now = datetime.now()
    next_minute = now + timedelta(minutes=1, seconds=10)  # 1分10秒后
    return next_minute.strftime("%H:%M")


async def test_scheduler():
    """测试定时调度器"""
    print("⏰ 测试定时发送功能")
    print("=" * 70)

    # 1. 显示当前配置
    print("1️⃣ 当前配置:")
    config_path = PROJECT_ROOT / "data" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    original_time = config.get('delivery', {}).get('time', '08:00')
    enabled = config.get('delivery', {}).get('enabled', True)
    user_email = config.get('user', {}).get('email')

    print(f"  推送时间: {original_time}")
    print(f"  启用状态: {enabled}")
    print(f"  接收邮箱: {user_email}")

    if not enabled:
        print("\n⚠️  定时推送未启用！")
        print("   请在 config.yaml 中设置 delivery.enabled: true")
        return

    # 2. 临时修改推送时间
    print(f"\n2️⃣ 临时修改推送时间...")
    new_time = get_next_minute()
    print(f"  原时间: {original_time}")
    print(f"  新时间: {new_time} (将在1分10秒后触发)")

    # 备份原配置
    import shutil
    backup_path = config_path.with_suffix('.yaml.bak')
    shutil.copy(config_path, backup_path)
    print(f"  已备份原配置到: {backup_path.name}")

    # 修改配置
    config['delivery']['time'] = new_time

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)

    # 3. 启动调度器
    print(f"\n3️⃣ 启动调度器...")
    from app.services.scheduler import SchedulerService

    scheduler = SchedulerService()
    scheduler.init_database()

    print(f"  调度器已创建，将在 {new_time} 触发")
    print(f"  当前时间: {datetime.now().strftime('%H:%M:%S')}")

    # 4. 等待触发
    print(f"\n4️⃣ 等待定时任务触发...")
    print(f"  ⏳ 请耐心等待... (最多等待120秒)")

    # 启动调度器
    import signal
    import os

    # 创建事件
    stop_event = asyncio.Event()

    def signal_handler(sig, frame):
        print("\n\n⚠️  收到中断信号，停止测试...")
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        scheduler.start(new_time)

        # 等待任务完成或超时
        # 我们需要等待下一个调度周期
        await asyncio.sleep(75)  # 等待75秒（应该足够触发）

    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
    finally:
        print("\n5️⃣ 停止调度器...")
        scheduler.stop()

    # 6. 恢复原配置
    print(f"\n6️⃣ 恢复原配置...")
    shutil.move(backup_path, config_path)
    print(f"  已恢复原配置时间: {original_time}")

    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print(f"\n📬 请检查邮箱: {user_email}")
    print(f"   如果收到邮件，说明定时发送功能正常！")


if __name__ == "__main__":
    try:
        asyncio.run(test_scheduler())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
