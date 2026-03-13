#!/bin/bash
# =============================================================================
# PersonalTeachers 代理配置脚本
# =============================================================================
# 功能：配置和管理服务的代理设置
# 用法：./scripts/proxy.sh [status|set|unset|auto]
#   status  - 查看当前代理状态
#   set     - 设置代理 (手动输入)
#   unset   - 取消代理
#   auto    - 自动检测系统代理
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
ENV_FILE="$BACKEND_DIR/.env"
BACKUP_ENV_FILE="$BACKEND_DIR/.env.backup"

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║   🌐 PersonalTeachers - 代理配置工具                    ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# 函数定义
# =============================================================================

# 显示当前代理状态
show_status() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📊 代理状态${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # 系统代理设置
    echo -e "${CYAN}系统代理设置:${NC}"

    local http_enable=$(scutil --proxy 2>/dev/null | grep HTTPEnable | awk '{print $3}')
    local https_enable=$(scutil --proxy 2>/dev/null | grep HTTPSEnable | awk '{print $3}')

    if [[ "$http_enable" == "1" ]]; then
        local http_host=$(scutil --proxy 2>/dev/null | grep HTTPProxy | awk '{print $3}')
        local http_port=$(scutil --proxy 2>/dev/null | grep HTTPPort | awk '{print $3}')
        echo -e "${GREEN}  HTTP 代理: ${NC}http://$http_host:$http_port"
    else
        echo -e "${YELLOW}  HTTP 代理: ${NC}未启用"
    fi

    if [[ "$https_enable" == "1" ]]; then
        local https_host=$(scutil --proxy 2>/dev/null | grep HTTPSProxy | awk '{print $3}')
        local https_port=$(scutil --proxy 2>/dev/null | grep HTTPSPort | awk '{print $3}')
        echo -e "${GREEN}  HTTPS 代理: ${NC}http://$https_host:$https_port"
    else
        echo -e "${YELLOW}  HTTPS 代理: ${NC}未启用"
    fi

    echo ""

    # 环境变量
    echo -e "${CYAN}当前环境变量:${NC}"
    if [ -n "$HTTP_PROXY" ] || [ -n "$http_proxy" ]; then
        echo -e "${GREEN}  HTTP_PROXY: ${NC}${HTTP_PROXY:-$http_proxy}"
    else
        echo -e "${YELLOW}  HTTP_PROXY: ${NC}未设置"
    fi

    if [ -n "$HTTPS_PROXY" ] || [ -n "$https_proxy" ]; then
        echo -e "${GREEN}  HTTPS_PROXY: ${NC}${HTTPS_PROXY:-$https_proxy}"
    else
        echo -e "${YELLOW}  HTTPS_PROXY: ${NC}未设置"
    fi

    if [ -n "$NO_PROXY" ] || [ -n "$no_proxy" ]; then
        echo -e "${GREEN}  NO_PROXY: ${NC}${NO_PROXY:-$no_proxy}"
    else
        echo -e "${YELLOW}  NO_PROXY: ${NC}未设置"
    fi

    echo ""

    # .env 文件中的代理设置
    echo -e "${CYAN}项目 .env 配置:${NC}"
    if [ -f "$ENV_FILE" ]; then
        if grep -q "^http_proxy=" "$ENV_FILE"; then
            local env_proxy=$(grep "^http_proxy=" "$ENV_FILE" | cut -d'=' -f2)
            if [ -n "$env_proxy" ]; then
                echo -e "${GREEN}  http_proxy: ${NC}$env_proxy"
            else
                echo -e "${YELLOW}  http_proxy: ${NC}已配置但为空"
            fi
        else
            echo -e "${YELLOW}  http_proxy: ${NC}未配置"
        fi

        if grep -q "^https_proxy=" "$ENV_FILE"; then
            local env_proxy=$(grep "^https_proxy=" "$ENV_FILE" | cut -d'=' -f2)
            if [ -n "$env_proxy" ]; then
                echo -e "${GREEN}  https_proxy: ${NC}$env_proxy"
            else
                echo -e "${YELLOW}  https_proxy: ${NC}已配置但为空"
            fi
        else
            echo -e "${YELLOW}  https_proxy: ${NC}未配置"
        fi
    else
        echo -e "${RED}  .env 文件不存在${NC}"
    fi

    echo ""

    # 测试连接
    echo -e "${CYAN}连接测试:${NC}"
    if command -v curl > /dev/null 2>&1; then
        local test_url="https://www.google.com"
        if curl -s --head --connect-timeout 5 "$test_url" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✅ 外网连接正常${NC}"
        else
            echo -e "${RED}  ❌ 外网连接失败${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠️  curl 命令不可用，无法测试连接${NC}"
    fi

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 自动检测并设置系统代理
auto_detect_proxy() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔍 自动检测系统代理${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    local http_enable=$(scutil --proxy 2>/dev/null | grep HTTPEnable | awk '{print $3}')

    if [[ "$http_enable" == "1" ]]; then
        local http_host=$(scutil --proxy 2>/dev/null | grep HTTPProxy | awk '{print $3}')
        local http_port=$(scutil --proxy 2>/dev/null | grep HTTPPort | awk '{print $3}')

        if [ -n "$http_host" ] && [ -n "$http_port" ]; then
            local proxy_url="http://$http_host:$http_port"
            echo -e "${GREEN}检测到系统代理: $proxy_url${NC}"

            # 更新 .env 文件
            update_env_proxy "$proxy_url" "$proxy_url"
            echo -e "${GREEN}✅ 代理配置已更新${NC}"

            # 询问是否重启服务
            echo ""
            read -p "$(echo -e ${CYAN}是否立即重启服务以应用代理配置? [y/N]: ${NC})" restart
            if [[ "$restart" =~ ^[Yy]$ ]]; then
                bash "$SCRIPT_DIR/stop.sh" > /dev/null 2>&1
                sleep 1
                bash "$SCRIPT_DIR/start.sh" production > /dev/null 2>&1
                echo -e "${GREEN}✅ 服务已重启${NC}"
            fi

            return 0
        fi
    fi

    echo -e "${YELLOW}未检测到系统代理${NC}"
    return 1
}

# 手动设置代理
manual_set_proxy() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}⚙️  手动设置代理${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    echo -e "${CYAN}常见代理配置示例:${NC}"
    echo -e "  Clash:       127.0.0.1:7890"
    echo -e "  V2Ray:       127.0.0.1:10809"
    echo -e "  Shadowsocks: 127.0.0.1:1080"
    echo ""

    read -p "$(echo -e ${CYAN}请输入代理地址 [格式: host:port]: ${NC})" proxy_input

    if [ -z "$proxy_input" ]; then
        echo -e "${RED}❌ 代理地址不能为空${NC}"
        return 1
    fi

    # 验证格式
    if [[ ! "$proxy_input" =~ ^[a-zA-Z0-9._-]+:[0-9]+$ ]]; then
        echo -e "${RED}❌ 代理地址格式不正确${NC}"
        return 1
    fi

    local proxy_url="http://$proxy_input"
    echo -e "${GREEN}设置代理: $proxy_url${NC}"

    # 更新 .env 文件
    update_env_proxy "$proxy_url" "$proxy_url"

    echo -e "${GREEN}✅ 代理配置已更新${NC}"

    # 询问是否重启服务
    echo ""
    read -p "$(echo -e ${CYAN}是否立即重启服务以应用代理配置? [y/N]: ${NC})" restart
    if [[ "$restart" =~ ^[Yy]$ ]]; then
        bash "$SCRIPT_DIR/stop.sh" > /dev/null 2>&1
        sleep 1
        bash "$SCRIPT_DIR/start.sh" production > /dev/null 2>&1
        echo -e "${GREEN}✅ 服务已重启${NC}"
    fi
}

# 取消代理设置
unset_proxy() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚫 取消代理设置${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ .env 文件不存在${NC}"
        return 1
    fi

    # 备份原文件
    cp "$ENV_FILE" "$BACKUP_ENV_FILE"

    # 移除代理配置
    sed -i '' '/^http_proxy=/d' "$ENV_FILE"
    sed -i '' '/^https_proxy=/d' "$ENV_FILE"
    sed -i '' '/^no_proxy=/d' "$ENV_FILE"
    sed -i '' '/^HTTP_PROXY=/d' "$ENV_FILE"
    sed -i '' '/^HTTPS_PROXY=/d' "$ENV_FILE"
    sed -i '' '/^NO_PROXY=/d' "$ENV_FILE"

    echo -e "${GREEN}✅ 代理配置已移除${NC}"
    echo -e "${CYAN}备份文件: $BACKUP_ENV_FILE${NC}"

    # 询问是否重启服务
    echo ""
    read -p "$(echo -e ${CYAN}是否立即重启服务以应用配置? [y/N]: ${NC})" restart
    if [[ "$restart" =~ ^[Yy]$ ]]; then
        bash "$SCRIPT_DIR/stop.sh" > /dev/null 2>&1
        sleep 1
        bash "$SCRIPT_DIR/start.sh" production > /dev/null 2>&1
        echo -e "${GREEN}✅ 服务已重启${NC}"
    fi
}

# 更新 .env 文件中的代理配置
update_env_proxy() {
    local http_proxy="$1"
    local https_proxy="$2"
    local no_proxy="${3:-localhost,127.0.0.1}"

    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ .env 文件不存在${NC}"
        return 1
    fi

    # 备份原文件
    cp "$ENV_FILE" "$BACKUP_ENV_FILE"

    # 移除旧的代理配置
    sed -i '' '/^http_proxy=/d' "$ENV_FILE"
    sed -i '' '/^https_proxy=/d' "$ENV_FILE"
    sed -i '' '/^no_proxy=/d' "$ENV_FILE"

    # 添加新的代理配置
    echo "" >> "$ENV_FILE"
    echo "# 代理配置 (由 proxy.sh 脚本管理)" >> "$ENV_FILE"
    echo "http_proxy=$http_proxy" >> "$ENV_FILE"
    echo "https_proxy=$https_proxy" >> "$ENV_FILE"
    echo "no_proxy=$no_proxy" >> "$ENV_FILE"
}

# 显示帮助信息
show_help() {
    echo -e "${CYAN}用法: ./scripts/proxy.sh [command]${NC}"
    echo ""
    echo -e "${CYAN}命令:${NC}"
    echo -e "  ${GREEN}status${NC}    查看当前代理状态"
    echo -e "  ${GREEN}set${NC}       手动设置代理"
    echo -e "  ${GREEN}unset${NC}     取消代理设置"
    echo -e "  ${GREEN}auto${NC}      自动检测并设置系统代理"
    echo -e "  ${GREEN}help${NC}      显示此帮助信息"
    echo ""
    echo -e "${CYAN}示例:${NC}"
    echo -e "  ./scripts/proxy.sh status"
    echo -e "  ./scripts/proxy.sh auto"
    echo -e "  ./scripts/proxy.sh set"
    echo -e "  ./scripts/proxy.sh unset"
}

# =============================================================================
# 主程序
# =============================================================================

# 如果没有参数，显示状态
if [ $# -eq 0 ]; then
    show_status
    exit 0
fi

# 解析命令
COMMAND="$1"
case "$COMMAND" in
    status)
        show_status
        ;;
    set)
        manual_set_proxy
        ;;
    unset)
        unset_proxy
        ;;
    auto)
        auto_detect_proxy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ 未知命令: $COMMAND${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac