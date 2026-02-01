#!/usr/bin/env python3
"""
恢复原推送时间配置
"""
import sys
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def restore_delivery_time():
    """恢复推送时间为08:00"""
    config_path = PROJECT_ROOT / "data" / "config.yaml"

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    current_time = config.get('delivery', {}).get('time', '08:00')

    # 恢复为08:00
    config['delivery']['time'] = '08:00'

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"✅ 已恢复推送时间: {current_time} → 08:00")
    print("📅 每天早上8点将自动发送语录")


if __name__ == "__main__":
    print("=" * 50)
    print("🔄 恢复推送时间")
    print("=" * 50)
    restore_delivery_time()
