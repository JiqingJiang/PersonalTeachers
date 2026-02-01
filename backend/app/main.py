"""
PersonalTeachers FastAPI应用入口

这是Web服务的启动文件，整合所有API和定时任务
"""
import os
import yaml
from contextlib import asynccontextmanager
from pathlib import Path

# 加载环境变量（必须在其他导入之前）
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api import api_router
from app.services import get_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("🚀 Starting PersonalTeachers...")

    # 初始化数据库
    db_path = Path(__file__).parent.parent / "storage" / "quotes.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    from app.models.database import Base
    from sqlalchemy import create_engine
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    logger.info("💾 Database initialized")

    # 启动定时任务
    try:
        config = _load_config()
        delivery_time = config.get('delivery', {}).get('time', '08:00')
        delivery_enabled = config.get('delivery', {}).get('enabled', True)

        if delivery_enabled:
            scheduler = get_scheduler()
            scheduler.init_database()
            scheduler.start(delivery_time)
            logger.info(f"⏰ Scheduler started (daily at {delivery_time})")
        else:
            logger.info("⏰ Scheduler disabled in config")
    except Exception as e:
        logger.warning(f"⚠️  Failed to start scheduler: {e}")

    yield

    # 关闭时
    logger.info("🛑 Shutting down PersonalTeachers...")
    try:
        scheduler = get_scheduler()
        scheduler.stop()
    except:
        pass


def _load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "data" / "config.yaml"

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# 创建FastAPI应用
app = FastAPI(
    title="PersonalTeachers API",
    description="人生导师每日推送系统 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

# 静态文件服务
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# 根路径
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页"""
    index_path = Path(__file__).parent.parent / "static" / "index.html"
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>PersonalTeachers</title>
        <style>
            body { font-family: -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .container { text-align: center; color: white; }
            h1 { font-size: 3em; margin: 0 0 20px 0; }
            p { font-size: 1.2em; opacity: 0.9; }
            .btn { display: inline-block; padding: 15px 30px; background: white; color: #667eea; text-decoration: none; border-radius: 30px; margin-top: 30px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 PersonalTeachers</h1>
            <p>人生导师每日推送系统</p>
            <a href="/docs" class="btn">查看 API 文档</a>
        </div>
    </body>
    </html>
    """


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "PersonalTeachers",
        "version": "1.0.0"
    }


# 首页路由
@app.get("/home", response_class=HTMLResponse)
async def home():
    """返回主页（备用路由）"""
    return await root()


# HTML页面路由
@app.get("/preferences.html", response_class=HTMLResponse)
async def preferences_page():
    """返回偏好设置页面"""
    preferences_path = Path(__file__).parent.parent / "static" / "preferences.html"
    if preferences_path.exists():
        with open(preferences_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Page not found</h1>", 404


@app.get("/history.html", response_class=HTMLResponse)
async def history_page():
    """返回历史语录页面"""
    history_path = Path(__file__).parent.parent / "static" / "history.html"
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Page not found</h1>", 404


if __name__ == "__main__":
    import uvicorn

    # 加载配置
    config = _load_config()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"🚀 Starting server at http://{host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
