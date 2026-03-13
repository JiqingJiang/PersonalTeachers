#!/bin/bash
# =============================================================================
# PersonalTeachers 服务启动脚本
# =============================================================================
# 功能：启动 FastAPI 后台服务和定时任务
# 用法：./scripts/start.sh [production|development]
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
PID_FILE="$PROJECT_ROOT/backend/app.pid"
LOG_FILE="$PROJECT_ROOT/backend/storage/logs/server.log"

# 解析参数
MODE="${1:-development}"
if [[ "$MODE" != "production" && "$MODE" != "development" ]]; then
    echo -e "${RED}错误: 模式必须是 'production' 或 'development'${NC}"
    exit 1
fi

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║   📚 PersonalTeachers - 服务启动脚本                  ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  服务已在运行 (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}如需重启，请先运行: ./scripts/stop.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}🧹 清理过期的 PID 文件${NC}"
        rm -f "$PID_FILE"
    fi
fi

# 2. 进入后端目录
cd "$BACKEND_DIR"

# 3. 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 虚拟环境不存在，请先创建: python -m venv venv${NC}"
    exit 1
fi

# 4. 激活虚拟环境
echo -e "${GREEN}🔧 激活虚拟环境...${NC}"
source venv/bin/activate

# 5. 检查依赖
echo -e "${GREEN}📦 检查依赖...${NC}"
pip install -q -r requirements.txt

# 6. 创建必要的目录
mkdir -p storage/logs
mkdir -p storage

# 7. 检查环境变量配置
echo -e "${GREEN}🔍 检查配置...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env 文件不存在！请先配置环境变量${NC}"
    exit 1
fi

# 检查关键的邮件配置
if grep -q "your-key-here\|your-group-id-here" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  警告: .env 中存在未配置的占位符${NC}"
fi

# 检查 SMTP 配置
SMTP_HOST=$(grep SMTP_HOST .env | cut -d'=' -f2)
SMTP_USERNAME=$(grep SMTP_USERNAME .env | cut -d'=' -f2)
SMTP_PASSWORD=$(grep SMTP_PASSWORD .env | cut -d'=' -f2)

if [ -z "$SMTP_HOST" ] || [ -z "$SMTP_USERNAME" ] || [ -z "$SMTP_PASSWORD" ]; then
    echo -e "${RED}❌ 邮件配置不完整，请检查 .env 文件${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SMTP: $SMTP_HOST | 用户: $SMTP_USERNAME${NC}"

# 8. 启动服务
echo ""
echo -e "${GREEN}🚀 启动服务 (模式: $MODE)...${NC}"

if [ "$MODE" = "production" ]; then
    # 生产模式：后台运行，不自动重载
    nohup python -m uvicorn app.main:app \
        --host 127.0.0.1 \
        --port 8000 \
        --log-level info \
        >> "$LOG_FILE" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"

    # 等待服务启动
    sleep 3

    # 检查服务是否成功启动
    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}✅ 服务启动成功！${NC}"
        echo -e "${GREEN}   PID: $PID${NC}"
        echo -e "${GREEN}   日志: $LOG_FILE${NC}"
    else
        echo -e "${RED}❌ 服务启动失败，请查看日志${NC}"
        rm -f "$PID_FILE"
        exit 1
    fi
else
    # 开发模式：前台运行，自动重载
    echo -e "${YELLOW}📝 开发模式: 服务在前台运行，Ctrl+C 停止${NC}"
    echo ""
    python -m uvicorn app.main:app \
        --host 127.0.0.1 \
        --port 8000 \
        --reload \
        --log-level info
fi

# 9. 显示访问信息
if [ "$MODE" = "production" ]; then
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}🌐 访问地址: http://localhost:8000${NC}"
    echo -e "${GREEN}📖 API文档: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}📊 状态检查: ./scripts/status.sh${NC}"
    echo -e "${GREEN}🛑 停止服务: ./scripts/stop.sh${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
fi
