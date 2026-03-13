#!/bin/bash

# PersonalTeachers 系统级服务安装脚本
# 此脚本需要sudo权限

set -e

echo "=========================================="
echo "  PersonalTeachers 系统级服务安装"
echo "=========================================="
echo ""

# 1. 停止用户级服务
echo "1️⃣  停止用户级服务..."
systemctl --user stop personalteachers.service 2>/dev/null || true
systemctl --user disable personalteachers.service 2>/dev/null || true
echo "   ✅ 用户级服务已停止"
echo ""

# 2. 复制服务文件
echo "2️⃣  安装系统级服务文件..."
sudo cp /home/jiqing/PersonalTeachers/personalteachers-system.service /etc/systemd/system/personalteachers.service
echo "   ✅ 服务文件已复制"
echo ""

# 3. 重载systemd配置
echo "3️⃣  重载systemd配置..."
sudo systemctl daemon-reload
echo "   ✅ 配置已重载"
echo ""

# 4. 启用服务
echo "4️⃣  启用服务（开机自启）..."
sudo systemctl enable personalteachers.service
echo "   ✅ 服务已启用"
echo ""

# 5. 启动服务
echo "5️⃣  启动服务..."
sudo systemctl start personalteachers.service
echo "   ✅ 服务已启动"
echo ""

# 6. 显示服务状态
echo "6️⃣  服务状态："
echo "=========================================="
sudo systemctl status personalteachers.service --no-pager
echo "=========================================="
echo ""

# 7. 显示日志
echo "7️⃣  最近日志："
echo "=========================================="
sudo journalctl -u personalteachers.service -n 20 --no-pager
echo "=========================================="
echo ""

echo "✅ 安装完成！"
echo ""
echo "📌 现在您可以安全退出SSH，服务会持续运行"
echo "📌 查看服务状态: sudo systemctl status personalteachers.service"
echo "📌 查看实时日志: sudo journalctl -u personalteachers.service -f"
echo "📌 重启服务: sudo systemctl restart personalteachers.service"
echo "📌 停止服务: sudo systemctl stop personalteachers.service"
