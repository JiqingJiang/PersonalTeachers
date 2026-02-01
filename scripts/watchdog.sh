#!/bin/bash
# =============================================================================
# PersonalTeachers 看门狗脚本
# =============================================================================
# 功能：监控服务状态，网络变化时自动恢复，服务崩溃时重启
# 用法：./scripts/watchdog.sh [--daemon]
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
PID_FILE="$PROJECT_ROOT/backend/app.pid"
WATCHDOG_PID_FILE="$PROJECT_ROOT/backend/watchdog.pid"
LOG_FILE="$PROJECT_ROOT/backend/storage/logs/watchdog.log"
CHECK_INTERVAL=60  # 检查间隔（秒）

# 解析参数
DAEMON_MODE=false
if [[ "$1" == "--daemon" ]]; then
    DAEMON_MODE=true
fi

# =============================================================================
# 日志函数
# =============================================================================
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
}

log_warn() {
    log "WARN" "$@"
}

log_error() {
    log "ERROR" "$@"
}

# =============================================================================
# 网络检测函数
# =============================================================================
check_network() {
    # 检查本地端口监听
    if ! lsof -i :8000 > /dev/null 2>&1; then
        return 1
    fi

    # 检查 HTTP 健康端点
    if command -v curl > /dev/null 2>&1; then
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8000/health 2>/dev/null || echo "000")
        if [ "$http_code" != "200" ]; then
            return 1
        fi
    fi

    return 0
}

check_internet() {
    # 检查外网连接
    if command -v curl > /dev/null 2>&1; then
        # 尝试连接多个可靠的公共服务
        local hosts=("8.8.8.8" "1.1.1.1" "223.5.5.5")
        for host in "${hosts[@]}"; do
            if ping -c 1 -W 2 "$host" > /dev/null 2>&1; then
                return 0
            fi
        done
        return 1
    fi
    return 0  # 无法检测时假设网络正常
}

get_current_network() {
    # 获取当前网络信息
    local wifi_name=$(networksetup -getairportnetwork en0 2>/dev/null | awk -F': ' '{print $2}' || echo "Unknown")
    local ip_address=$(ipconfig getifaddr en0 2>/dev/null || echo "N/A")
    echo "WiFi: $wifi_name | IP: $ip_address"
}

# =============================================================================
# 服务管理函数
# =============================================================================
is_service_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # 尝试通过进程名查找
    local pids=$(ps aux | grep -v grep | grep "uvicorn app.main:app" | awk '{print $2}')
    if [ -n "$pids" ]; then
        return 0
    fi

    return 1
}

start_service() {
    log_info "🔄 启动服务..."
    cd "$PROJECT_ROOT"
    bash "$SCRIPT_DIR/start.sh" production > /dev/null 2>&1

    # 等待服务启动
    local max_wait=30
    local waited=0
    while [ $waited -lt $max_wait ]; do
        if check_network; then
            log_info "✅ 服务启动成功"
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
    done

    log_error "❌ 服务启动失败（等待 $max_wait 秒后仍无响应）"
    return 1
}

stop_service() {
    log_info "🛑 停止服务..."
    cd "$PROJECT_ROOT"
    bash "$SCRIPT_DIR/stop.sh" > /dev/null 2>&1
    sleep 2
}

restart_service() {
    log_warn "🔄 重启服务..."
    stop_service
    sleep 2
    start_service
}

# =============================================================================
# 代理检测函数
# =============================================================================
check_proxy_settings() {
    # 检测系统代理设置
    local http_proxy=$(scutil --proxy 2>/dev/null | grep HTTPProxy | awk '{print $3}')
    local https_proxy=$(scutil --proxy 2>/dev/null | grep HTTPSProxy | awk '{print $3}')
    local http_enable=$(scutil --proxy 2>/dev/null | grep HTTPEnable | awk '{print $3}')
    local https_enable=$(scutil --proxy 2>/dev/null | grep HTTPSEnable | awk '{print $3}')

    if [[ "$http_enable" == "1" ]] && [[ -n "$http_proxy" ]]; then
        log_info "🌐 检测到系统 HTTP 代理: $http_proxy"
        export http_proxy="http://$http_proxy"
        export https_proxy="http://$https_proxy"
        return 0
    fi

    # 清除代理环境变量
    unset http_proxy
    unset https_proxy
    unset HTTP_PROXY
    unset HTTPS_PROXY

    return 1
}

# =============================================================================
# 健康检查函数
# =============================================================================
health_check() {
    local errors=0

    # 1. 检查进程
    if ! is_service_running; then
        log_error "❌ 服务进程未运行"
        errors=$((errors + 1))
    fi

    # 2. 检查网络监听
    if ! lsof -i :8000 > /dev/null 2>&1; then
        log_error "❌ 端口 8000 未监听"
        errors=$((errors + 1))
    fi

    # 3. 检查 HTTP 健康端点
    if command -v curl > /dev/null 2>&1; then
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8000/health 2>/dev/null || echo "000")
        if [ "$http_code" != "200" ]; then
            log_error "❌ 健康检查失败 (HTTP $http_code)"
            errors=$((errors + 1))
        fi
    fi

    # 4. 检查外网连接
    if ! check_internet; then
        log_warn "⚠️  外网连接不可用"
    fi

    return $errors
}

# =============================================================================
# 主循环
# =============================================================================
main_loop() {
    local last_network=""
    local network_failures=0
    local max_network_failures=3

    log_info "════════════════════════════════════════════════════════"
    log_info "🐕 PersonalTeachers 看门狗启动"
    log_info "════════════════════════════════════════════════════════"

    while true; do
        # 获取当前网络信息
        local current_network=$(get_current_network)

        # 检测网络变化
        if [ "$current_network" != "$last_network" ]; then
            log_info "🌐 网络变化检测: $current_network"
            last_network="$current_network"

            # 检查代理设置
            check_proxy_settings

            # 网络变化后等待一下再检查服务
            sleep 3
        fi

        # 执行健康检查
        if health_check; then
            # 服务正常，重置失败计数
            network_failures=0
        else
            network_failures=$((network_failures + 1))
            log_error "❌ 健康检查失败 (第 $network_failures/$max_network_failures 次)"

            if [ $network_failures -ge $max_network_failures ]; then
                log_error "🚨 连续 $max_network_failures 次健康检查失败，尝试重启服务..."
                restart_service
                network_failures=0
                last_network=$(get_current_network)  # 重启后更新网络信息
            fi
        fi

        # 等待下次检查
        sleep $CHECK_INTERVAL
    done
}

# =============================================================================
# 信号处理
# =============================================================================
cleanup() {
    log_info "🐕 看门狗停止"
    rm -f "$WATCHDOG_PID_FILE"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# 主程序
# =============================================================================
if [ "$DAEMON_MODE" = true ]; then
    # 后台模式
    if [ -f "$WATCHDOG_PID_FILE" ]; then
        old_pid=$(cat "$WATCHDOG_PID_FILE")
        if ps -p "$old_pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  看门狗已在运行 (PID: $old_pid)${NC}"
            exit 1
        fi
    fi

    # 启动后台守护进程
    nohup "$0" > /dev/null 2>&1 &
    echo $! > "$WATCHDOG_PID_FILE"

    echo -e "${GREEN}✅ 看门狗已在后台启动 (PID: $!)${NC}"
    echo -e "${CYAN}查看日志: tail -f $LOG_FILE${NC}"
    echo -e "${CYAN}停止看门狗: kill $(cat $WATCHDOG_PID_FILE)${NC}"
    exit 0
fi

# 前台模式：启动主循环
# 检查是否已有实例在运行
if [ -f "$WATCHDOG_PID_FILE" ]; then
    old_pid=$(cat "$WATCHDOG_PID_FILE")
    if ps -p "$old_pid" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  看门狗已在运行 (PID: $old_pid)${NC}"
        echo -e "${CYAN}使用 --daemon 参数启动后台模式${NC}"
        exit 1
    fi
fi

# 记录 PID
echo $$ > "$WATCHDOG_PID_FILE"

# 首次启动时确保服务运行
if ! is_service_running; then
    echo -e "${YELLOW}⚠️  服务未运行，正在启动...${NC}"
    start_service
fi

# 启动主循环
main_loop