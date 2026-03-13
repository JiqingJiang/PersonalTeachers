#!/usr/bin/env python3
"""
PersonalTeachers 主启动脚本
运行此脚本启动Web服务和定时任务
"""
import uvicorn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """启动FastAPI应用"""
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   📚 PersonalTeachers - 人生导师每日推送系统              ║
║                                                       ║
║   通过多元化虚拟导师的每日智慧推送                         ║
║   建立360度认知体系                                     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)

    # 从环境变量读取配置
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    print("🚀 启动服务...")
    print(f"📁 项目路径: {PROJECT_ROOT}")
    print(f"🌐 访问地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print("")

    # 启动FastAPI应用
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,  # 生产环境关闭自动重载
        log_level="info"
    )


if __name__ == "__main__":
    main()
