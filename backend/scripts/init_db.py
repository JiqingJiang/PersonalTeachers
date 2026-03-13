#!/usr/bin/env python3
"""
数据库初始化脚本
创建SQLite数据库和表结构
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.models.database import Base
from sqlalchemy import create_engine
from loguru import logger


def init_database():
    """初始化数据库"""
    db_path = PROJECT_ROOT / "storage" / "quotes.db"

    # 确保storage目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"📁 数据库路径: {db_path}")

    # 创建数据库引擎
    engine = create_engine(f"sqlite:///{db_path}")

    # 创建所有表
    Base.metadata.create_all(engine)

    logger.success("✅ 数据库初始化完成！")
    logger.info(f"📊 数据库文件: {db_path}")

    return engine


if __name__ == "__main__":
    logger.info("🚀 开始初始化数据库...")
    init_database()
