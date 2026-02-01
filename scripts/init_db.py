#!/usr/bin/env python3
"""
数据库初始化脚本

创建SQLite数据库和表结构
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from sqlalchemy import create_engine
from app.models.database import Base


def init_database():
    """初始化数据库"""
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                           ║
║   💾 PersonalTeachers 数据库初始化                      ║
║                                                           ║
╚═══════════════════════════════════════════════════════╝
    """)

    # 数据库路径
    db_path = PROJECT_ROOT / "backend" / "storage" / "quotes.db"

    print(f"📁 数据库路径: {db_path}")

    # 确保存储目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建引擎
    engine = create_engine(f"sqlite:///{db_path}")

    print("🔧 创建表结构...")

    # 创建所有表
    Base.metadata.create_all(engine)

    print("✅ 数据库初始化完成！")
    print(f"\n📊 已创建的表:")
    print("   - quotes (语录表)")
    print("   - email_logs (邮件发送日志表)")

    print(f"\n💡 提示: 可以使用SQLite工具查看数据库:")
    print(f"   sqlite3 {db_path}")


if __name__ == "__main__":
    init_database()
