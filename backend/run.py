#!/usr/bin/env python3
"""
PersonalTeachers 主启动脚本
运行此脚本启动Web服务和定时任务
"""
import uvicorn
import sys
from pathlib import Path

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

    print("🚀 启动服务...")
    print(f"📁 项目路径: {PROJECT_ROOT}")
    print(f"🌐 访问地址: http://localhost:8000")
    print(f"📖 API文档: http://localhost:8000/docs")
    print("")

    # 启动FastAPI应用
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # 开发模式，代码改动自动重载
        log_level="info"
    )


if __name__ == "__main__":
    main()
