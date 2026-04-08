#!/bin/bash
set -e

# PersonalTeachers v2 部署脚本
# 用法: bash deploy.sh [init|update]

APP_DIR="/opt/personalteachers"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

ACTION="${1:-update}"

echo "=== PersonalTeachers v2 部署 ==="
echo "动作: $ACTION"
echo "项目目录: $PROJECT_DIR"
echo "部署目录: $APP_DIR"
echo ""

# --- 初始化 ---
if [ "$ACTION" = "init" ]; then
    echo "[1/6] 创建部署目录..."
    mkdir -p $APP_DIR/{backend,frontend,admin}

    echo "[2/6] 安装系统依赖..."
    apt-get update -qq
    apt-get install -y -qq python3 python3-venv python3-pip nginx

    echo "[3/6] 创建 Python 虚拟环境..."
    python3 -m venv $APP_DIR/backend/venv
    $APP_DIR/backend/venv/bin/pip install --upgrade pip -q

    echo "[4/6] 复制后端代码..."
    cp -r $PROJECT_DIR/backend/app $APP_DIR/backend/
    cp -r $PROJECT_DIR/backend/data $APP_DIR/backend/
    cp -r $PROJECT_DIR/backend/templates $APP_DIR/backend/
    cp $PROJECT_DIR/backend/run.py $APP_DIR/backend/
    cp $PROJECT_DIR/backend/requirements.txt $APP_DIR/backend/
    cp $PROJECT_DIR/backend/pytest.ini $APP_DIR/backend/

    echo "[5/6] 安装 Python 依赖..."
    $APP_DIR/backend/venv/bin/pip install -r $APP_DIR/backend/requirements.txt -q

    # 创建 .env（如果不存在）
    if [ ! -f $APP_DIR/backend/.env ]; then
        cp $PROJECT_DIR/backend/.env.example $APP_DIR/backend/.env
        echo ""
        echo "⚠️  请编辑 $APP_DIR/backend/.env 填写配置！"
        echo "   必填: SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD"
        echo ""
    fi

    echo "[6/6] 配置 systemd 和 Nginx..."
    cp $PROJECT_DIR/deploy/personalteachers.service /etc/systemd/system/
    cp $PROJECT_DIR/deploy/nginx.conf /etc/nginx/sites-available/personalteachers
    ln -sf /etc/nginx/sites-available/personalteachers /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    systemctl daemon-reload
    systemctl enable personalteachers

    echo ""
    echo "=== 初始化完成 ==="
    echo "后续步骤:"
    echo "  1. 编辑 $APP_DIR/backend/.env"
    echo "  2. bash $SCRIPT_DIR/deploy.sh update"
    echo ""
fi

# --- 更新部署 ---
if [ "$ACTION" = "update" ]; then
    echo "[1/5] 更新后端代码..."
    cp -r $PROJECT_DIR/backend/app $APP_DIR/backend/
    cp -r $PROJECT_DIR/backend/data $APP_DIR/backend/
    cp -r $PROJECT_DIR/backend/templates $APP_DIR/backend/
    cp $PROJECT_DIR/backend/run.py $APP_DIR/backend/
    cp $PROJECT_DIR/backend/requirements.txt $APP_DIR/backend/

    echo "[2/5] 更新 Python 依赖..."
    $APP_DIR/backend/venv/bin/pip install -r $APP_DIR/backend/requirements.txt -q

    echo "[3/5] 构建前端..."
    cd $PROJECT_DIR/frontend
    npm install --quiet
    npm run build
    rm -rf $APP_DIR/frontend/*
    cp -r dist/* $APP_DIR/frontend/

    echo "[4/5] 构建管理后台..."
    cd $PROJECT_DIR/admin
    npm install --quiet
    npm run build
    rm -rf $APP_DIR/admin/*
    cp -r dist/* $APP_DIR/admin/

    echo "[5/5] 重启服务..."
    systemctl restart personalteachers
    nginx -t && systemctl reload nginx

    echo ""
    echo "=== 部署完成 ==="
    systemctl status personalteachers --no-pager -l | head -10
    echo ""
    echo "访问地址:"
    echo "  用户端: http://$(hostname -I | awk '{print $1}')/"
    echo "  管理后台: http://$(hostname -I | awk '{print $1}')/admin/"
    echo ""
fi

# --- 查看日志 ---
if [ "$ACTION" = "logs" ]; then
    journalctl -u personalteachers -f --no-pager
fi
