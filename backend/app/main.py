"""FastAPI 应用工厂"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库和种子数据"""
    logger.info("正在初始化数据库...")
    from app.models import init_db
    await init_db()

    # 导入所有模型确保表被创建
    import app.models  # noqa: F401

    # 再次确保所有表已创建
    from app.models.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 种子数据
    logger.info("正在检查种子数据...")
    from app.services.seed import seed_system_data
    await seed_system_data()

    # 启动推送调度器
    from app.services.push_scheduler import PushScheduler
    scheduler = PushScheduler()
    scheduler.start()

    logger.info("PersonalTeachers v2 启动完成")
    yield
    scheduler.stop()
    logger.info("PersonalTeachers v2 关闭")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.auth import router as auth_router
    from app.api.users import router as users_router
    from app.api.keywords import router as keywords_router
    from app.api.mentors import router as mentors_router
    from app.api.preferences import router as preferences_router
    from app.api.quotes import router as quotes_router

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["用户"])
    app.include_router(keywords_router, prefix="/api/v1/keywords", tags=["关键词"])
    app.include_router(mentors_router, prefix="/api/v1/mentors", tags=["导师"])
    app.include_router(preferences_router, prefix="/api/v1/preferences", tags=["偏好"])
    app.include_router(quotes_router, prefix="/api/v1/quotes", tags=["语录"])

    # 管理后台路由
    from app.api.admin.users import router as admin_users_router
    from app.api.admin.ai_models import router as admin_ai_router
    from app.api.admin.email_pool import router as admin_email_router
    from app.api.admin.stats import router as admin_stats_router

    app.include_router(admin_users_router, prefix="/api/v1/admin/users", tags=["管理-用户"])
    app.include_router(admin_ai_router, prefix="/api/v1/admin/ai-models", tags=["管理-AI模型"])
    app.include_router(admin_email_router, prefix="/api/v1/admin/email-pool", tags=["管理-邮箱池"])
    app.include_router(admin_stats_router, prefix="/api/v1/admin/stats", tags=["管理-统计"])

    @app.get("/api/v1/health")
    async def health_check():
        return {"status": "ok", "version": "2.0.0"}

    return app


app = create_app()
