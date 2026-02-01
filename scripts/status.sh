#!/bin/bash
# =============================================================================
# PersonalTeachers 服务状态检测脚本
# =============================================================================
# 功能：检测服务运行状态、配置有效性、邮件发送能力
# 用法：./scripts/status.sh [--verbose]
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
PID_FILE="$PROJECT_ROOT/backend/app.pid"
LOG_FILE="$PROJECT_ROOT/backend/storage/logs/server.log"

VERBOSE=false
if [[ "$1" == "--verbose" ]]; then
    VERBOSE=true
fi

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║   🔍 PersonalTeachers - 服务状态检测                 ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 检查函数
# =============================================================================

check_item() {
    local name="$1"
    local status="$2"
    local message="$3"

    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $name${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $name${NC}"
    elif [ "$status" = "ERROR" ]; then
        echo -e "${RED}❌ $name${NC}"
    else
        echo -e "${CYAN}ℹ️  $name${NC}"
    fi

    if [ -n "$message" ] && [ "$VERBOSE" = true ]; then
        echo -e "   ${CYAN}→ $message${NC}"
    fi
}

# =============================================================================
# 1. 进程状态检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 进程状态${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

SERVICE_RUNNING=false
SERVICE_PID=""

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        SERVICE_RUNNING=true
        SERVICE_PID="$PID"
        check_item "服务进程" "OK" "PID: $PID"
    else
        check_item "PID 文件存在但进程未运行" "WARN" "清理过期 PID 文件"
        rm -f "$PID_FILE"
    fi
else
    # 尝试通过进程名查找
    PIDS=$(ps aux | grep -v grep | grep "uvicorn app.main:app" | awk '{print $2}')
    if [ -n "$PIDS" ]; then
        SERVICE_RUNNING=true
        SERVICE_PID="$PIDS"
        check_item "服务进程运行中（未记录 PID）" "WARN" "PID: $PIDS"
    else
        check_item "服务未运行" "ERROR" "请使用 ./scripts/start.sh 启动服务"
    fi
fi

# 显示进程详情
if [ "$SERVICE_RUNNING" = true ] && [ "$VERBOSE" = true ]; then
    echo ""
    ps -p "$SERVICE_PID" -o pid,ppid,cmd,etime,stat || true
fi

echo ""

# =============================================================================
# 2. 端口监听检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌐 网络端口${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if lsof -i :8000 > /dev/null 2>&1; then
    LISTEN_INFO=$(lsof -i :8000 | tail -n +2 | head -1)
    check_item "端口 8000 监听中" "OK" "$LISTEN_INFO"
else
    check_item "端口 8000 未监听" "ERROR" "服务可能未正确启动"
fi

echo ""

# =============================================================================
# 3. API 健康检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🏥 API 健康检查${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$SERVICE_RUNNING" = true ]; then
    if command -v curl > /dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
        if [ "$HTTP_CODE" = "200" ]; then
            check_item "API 健康检查" "OK" "HTTP 200"
        else
            check_item "API 健康检查" "ERROR" "HTTP $HTTP_CODE"
        fi
    else
        check_item "curl 命令不可用" "WARN" "无法执行 HTTP 检查"
    fi
else
    check_item "API 健康检查" "SKIP" "服务未运行"
fi

echo ""

# =============================================================================
# 4. 环境配置检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}⚙️  环境配置${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ENV_FILE="$BACKEND_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    check_item ".env 文件" "OK" "配置文件存在"

    # 检查 AI 模型配置
    if grep -q "your-key-here\|your-group-id-here" "$ENV_FILE" 2>/dev/null; then
        check_item "AI 模型配置" "WARN" "存在未配置的占位符"
    else
        AI_KEYS=0
        grep -E "^(ZHIPUAI_API_KEY|DEEPSEEK_API_KEY|GEMINI_API_KEY|MINIMAX_API_KEY)=" "$ENV_FILE" | grep -v "your-key-here" > /dev/null && AI_KEYS=$(grep -cE "^[A-Z_]+API_KEY=.+" "$ENV_FILE" || echo 0)
        if [ "$AI_KEYS" -gt 0 ]; then
            check_item "AI 模型配置" "OK" "已配置 $AI_KEYS 个模型"
        else
            check_item "AI 模型配置" "WARN" "未配置任何模型"
        fi
    fi

    # 检查邮件配置
    SMTP_HOST=$(grep "^SMTP_HOST=" "$ENV_FILE" | cut -d'=' -f2)
    SMTP_PORT=$(grep "^SMTP_PORT=" "$ENV_FILE" | cut -d'=' -f2)
    SMTP_USERNAME=$(grep "^SMTP_USERNAME=" "$ENV_FILE" | cut -d'=' -f2)
    SMTP_PASSWORD=$(grep "^SMTP_PASSWORD=" "$ENV_FILE" | cut -d'=' -f2)
    EMAIL_FROM=$(grep "^EMAIL_FROM=" "$ENV_FILE" | cut -d'=' -f2)

    if [ -n "$SMTP_HOST" ] && [ -n "$SMTP_USERNAME" ] && [ -n "$SMTP_PASSWORD" ]; then
        check_item "邮件 SMTP 配置" "OK" "$SMTP_USERNAME @ $SMTP_HOST:$SMTP_PORT"
    else
        check_item "邮件 SMTP 配置" "ERROR" "配置不完整"
    fi

    if [ -n "$EMAIL_FROM" ]; then
        check_item "发件人邮箱" "OK" "$EMAIL_FROM"
    else
        check_item "发件人邮箱" "WARN" "未设置 EMAIL_FROM"
    fi
else
    check_item ".env 文件" "ERROR" "配置文件不存在"
fi

echo ""

# =============================================================================
# 5. YAML 配置检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 YAML 配置${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

CONFIG_FILE="$BACKEND_DIR/data/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    check_item "config.yaml" "OK" "配置文件存在"

    # 读取用户邮箱
    if command -v python3 > /dev/null 2>&1; then
        USER_EMAIL=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('user', {}).get('email', '未设置'))" 2>/dev/null || echo "解析失败")
        DELIVERY_ENABLED=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('delivery', {}).get('enabled', False))" 2>/dev/null || echo "false")
        DELIVERY_TIME=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE')).get('delivery', {}).get('time', '08:00'))" 2>/dev/null || echo "08:00")

        if [ "$USER_EMAIL" != "未设置" ] && [ "$USER_EMAIL" != "解析失败" ]; then
            check_item "用户邮箱" "OK" "$USER_EMAIL"
        else
            check_item "用户邮箱" "WARN" "$USER_EMAIL"
        fi

        if [ "$DELIVERY_ENABLED" = "True" ] || [ "$DELIVERY_ENABLED" = "true" ]; then
            check_item "定时推送" "OK" "已启用，每天 $DELIVERY_TIME"
        else
            check_item "定时推送" "WARN" "已禁用"
        fi
    fi
else
    check_item "config.yaml" "ERROR" "配置文件不存在"
fi

echo ""

# =============================================================================
# 6. 数据库检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}💾 数据库${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DB_FILE="$BACKEND_DIR/storage/quotes.db"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(ls -lh "$DB_FILE" | awk '{print $5}')
    check_item "SQLite 数据库" "OK" "大小: $DB_SIZE"

    if command -v sqlite3 > /dev/null 2>&1; then
        QUOTE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM quotes;" 2>/dev/null || echo "0")
        EMAIL_LOG_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM email_logs;" 2>/dev/null || echo "0")

        check_item "语录数量" "INFO" "$QUOTE_COUNT 条"
        check_item "邮件发送记录" "INFO" "$EMAIL_LOG_COUNT 条"

        # 检查最近的邮件发送状态
        if [ "$EMAIL_LOG_COUNT" -gt 0 ]; then
            LAST_EMAIL=$(sqlite3 "$DB_FILE" "SELECT success, sent_at FROM email_logs ORDER BY sent_at DESC LIMIT 1;" 2>/dev/null || echo "")
            if [ -n "$LAST_EMAIL" ]; then
                LAST_SUCCESS=$(echo "$LAST_EMAIL" | cut -d'|' -f1)
                LAST_TIME=$(echo "$LAST_EMAIL" | cut -d'|' -f2)
                if [ "$LAST_SUCCESS" = "1" ]; then
                    check_item "最近一次发送" "OK" "$LAST_TIME (成功)"
                else
                    check_item "最近一次发送" "WARN" "$LAST_TIME (失败)"
                fi
            fi
        fi
    else
        check_item "sqlite3 不可用" "WARN" "无法查询数据库详情"
    fi
else
    check_item "SQLite 数据库" "WARN" "数据库文件不存在（首次运行后自动创建）"
fi

echo ""

# =============================================================================
# 7. 日志检查
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📜 最近日志${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$LOG_FILE" ]; then
    check_item "日志文件" "OK" "$LOG_FILE"
    echo ""
    tail -n 10 "$LOG_FILE" | sed 's/^/   /' || true
else
    check_item "日志文件" "WARN" "日志文件不存在"
fi

echo ""

# =============================================================================
# 8. 总结和建议
# =============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📝 诊断总结${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$SERVICE_RUNNING" = false ]; then
    echo -e "${RED}⚠️  服务未运行${NC}"
    echo -e "${CYAN}   → 启动服务: ./scripts/start.sh${NC}"
    echo ""
fi

# 提示配置修改后需要重启
if [ "$SERVICE_RUNNING" = true ]; then
    echo -e "${GREEN}✅ 服务正在运行${NC}"
    echo -e "${YELLOW}   ⚠️  配置修改后需要重启服务: ./scripts/stop.sh && ./scripts/start.sh${NC}"
    echo ""
fi

# 显示常用命令
echo -e "${CYAN}常用命令:${NC}"
echo -e "${CYAN}  • 启动服务:     ./scripts/start.sh${NC}"
echo -e "${CYAN}  • 停止服务:     ./scripts/stop.sh${NC}"
echo -e "${CYAN}  • 查看详细日志: ./scripts/status.sh --verbose${NC}"
echo -e "${CYAN}  • 实时日志:     tail -f $LOG_FILE${NC}"
echo -e "${CYAN}  • 修改配置:     编辑 $BACKEND_DIR/data/config.yaml${NC}"
echo -e "${CYAN}  • 修改邮箱:     编辑 $BACKEND_DIR/.env${NC}"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
