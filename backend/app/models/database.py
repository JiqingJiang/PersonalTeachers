"""数据库引擎和会话管理"""

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

engine = None
async_session = None  # 兼容旧代码：async_sessionmaker 实例


class Base(DeclarativeBase):
    pass


async def init_db():
    """初始化数据库引擎和表"""
    global engine, async_session

    settings = get_settings()
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
    )
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 增量迁移：为已有表添加新列
    await _migrate_add_columns(async_session)


async def _migrate_add_columns(session_maker):
    """为已存在的表添加新列（安全操作，列已存在则跳过）"""
    migrations = [
        ("users", "push_count", "INTEGER DEFAULT 10"),
        ("users", "max_words", "INTEGER DEFAULT 100"),
        ("users", "personal_bio", "TEXT"),
        ("users", "personalization_weight", "FLOAT DEFAULT 0.5"),
    ]

    async with session_maker() as session:
        for table, column, col_type in migrations:
            try:
                await session.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                )
                await session.commit()
                logger.info(f"迁移成功: {table}.{column}")
            except Exception:
                # 列已存在，忽略
                await session.rollback()


async def get_session() -> AsyncSession:
    """获取数据库会话（用于依赖注入）"""
    if async_session is None:
        await init_db()
    async with async_session() as session:
        yield session
