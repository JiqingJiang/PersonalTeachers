"""数据库引擎和会话管理"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

engine = None
async_session = None


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


async def get_session() -> AsyncSession:
    """获取数据库会话（用于依赖注入）"""
    if async_session is None:
        await init_db()
    async with async_session() as session:
        yield session
