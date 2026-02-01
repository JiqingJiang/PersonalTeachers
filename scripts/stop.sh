#!/bin/bash
# =============================================================================
# PersonalTeachers 服务关闭脚本
# =============================================================================
# 功能：安全停止 FastAPI 后台服务
# 用法：./scripts/stop.sh
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

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║   🛑 PersonalTeachers - 服务关闭脚本                   ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. 检查 PID 文件是否存在
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  未找到 PID 文件，尝试查找运行中的进程...${NC}"

    # 尝试通过进程名查找
    PIDS=$(ps aux | grep -v grep | grep "uvicorn app.main:app" | awk '{print $2}')

    if [ -z "$PIDS" ]; then
        echo -e "${YELLOW}ℹ️  没有找到运行中的服务${NC}"
        exit 0
    else
        echo -e "${GREEN}🔍 找到运行中的服务进程${NC}"
        for PID in $PIDS; do
            echo -e "${YELLOW}   PID: $PID${NC}"
            echo $PID > "$PID_FILE"
        done
    fi
fi

# 2. 读取 PID
PID=$(cat "$PID_FILE")

# 3. 检查进程是否仍在运行
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  进程 $PID 未在运行${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

# 4. 尝试优雅关闭
echo -e "${GREEN}🔄 正在停止服务 (PID: $PID)...${NC}"

# 发送 TERM 信号
kill -TERM "$PID" 2>/dev/null || true

# 等待进程结束（最多 10 秒）
TIMEOUT=10
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务已优雅停止${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    echo -n "."
done

echo ""

# 5. 如果进程仍在运行，强制终止
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  进程未响应 TERM 信号，尝试强制终止...${NC}"
    kill -KILL "$PID" 2>/dev/null || true

    sleep 1

    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务已强制停止${NC}"
        rm -f "$PID_FILE"
    else
        echo -e "${RED}❌ 无法停止进程 $PID${NC}"
        exit 1
    fi
fi

# 6. 清理可能残留的 uvicorn 进程
echo -e "${GREEN}🧹 清理残留进程...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ 所有服务已停止${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"