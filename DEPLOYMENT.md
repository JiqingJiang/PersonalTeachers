# PersonalTeachers 部署指南

## 部署状态

✅ **部署成功** - PersonalTeachers 已成功部署到服务器并运行

### 服务器信息
- **公网 IP**: 123.56.81.224
- **域名**: erode.site
- **内网 IP**: 172.28.133.167
- **服务端口**: 8000
- **访问地址**:
  - http://123.56.81.224:8000
  - http://erode.site:8000

### 服务状态
- ✅ 服务运行中（systemd 用户级服务）
- ✅ 数据库已初始化（SQLite）
- ✅ 定时任务已配置（每天 08:25 发送邮件）
- ✅ 邮件服务已测试（QQ邮箱 SMTP）

---

## 从 macOS 访问 Dashboard

### 1. 直接访问（推荐使用域名）
在您的 macOS 浏览器中打开以下任一地址：
```
http://erode.site:8000
或
http://123.56.81.224:8000
```

### 2. 功能页面
- **首页仪表盘**: http://erode.site:8000/
- **偏好设置**: http://erode.site:8000/preferences
- **历史语录**: http://erode.site:8000/history
- **API 文档**: http://erode.site:8000/docs

### 3. 网络要求
- ✅ 域名已解析: erode.site → 123.56.81.224
- ✅ 防火墙已开放: 8000 端口可从公网访问
- 直接在浏览器输入地址即可访问

---

## 服务管理命令

### 查看服务状态
```bash
systemctl --user status personalteachers.service
```

### 启动服务
```bash
systemctl --user start personalteachers.service
```

### 停止服务
```bash
systemctl --user stop personalteachers.service
```

### 重启服务
```bash
systemctl --user restart personalteachers.service
```

### 查看日志
```bash
# 实时查看日志
journalctl --user -u personalteachers.service -f

# 查看最近 50 行日志
journalctl --user -u personalteachers.service -n 50
```

---

## 邮件配置

### 当前配置
- **SMTP 服务器**: smtp.qq.com
- **端口**: 465
- **发件人**: erode1701@qq.com
- **收件人**: erode1701@qq.com
- **推送时间**: 每天 08:25（北京时间）

### 修改推送时间
在 Web Dashboard 中访问"偏好设置"页面，修改"推送时间"配置。

---

## 防火墙配置（需要 root 权限）

如果需要从外部网络访问，需要配置防火墙：

```bash
# 使用 sudo 权限配置防火墙
sudo ufw allow 8000/tcp
sudo ufw reload
```

---

## 数据备份

### 数据库位置
```
/home/jiqing/PersonalTeachers/backend/storage/quotes.db
```

### 备份命令
```bash
# 创建备份
cp /home/jiqing/PersonalTeachers/backend/storage/quotes.db \
   /home/jiqing/PersonalTeachers/backend/storage/quotes.db.backup.$(date +%Y%m%d)

# 定期备份（可选）
crontab -e
# 添加以下行（每天凌晨 2 点备份）
0 2 * * * cp /home/jiqing/PersonalTeachers/backend/storage/quotes.db /home/jiqing/PersonalTeachers/backend/storage/quotes.db.backup.$(date +\%Y\%m\%d)
```

---

## 配置文件位置

### 环境变量
```
/home/jiqing/PersonalTeachers/backend/.env
```

### 应用配置
```
/home/jiqing/PersonalTeachers/backend/data/config.yaml
```

### 日志文件
```
/home/jiqing/PersonalTeachers/backend/storage/logs/app.log
```

---

## 服务自动重启

服务已配置为自动重启：
- 如果服务崩溃，systemd 会在 10 秒后自动重启
- 服务器重启后，服务会自动启动（已 enable）

---

## API 快速测试

### 测试邮件发送
```bash
curl -X POST http://erode.site:8000/api/email/test \
  -H "Content-Type: application/json" \
  -d '{"to_email": "erode1701@qq.com"}'
```

### 查看统计信息
```bash
curl http://erode.site:8000/api/stats
```

---

## 常见问题

### 1. 无法从 macOS 访问
- 检查网络连接: `ping erode.site` 或 `ping 123.56.81.224`
- 确认防火墙开放 8000 端口
- 尝试使用公网IP: http://123.56.81.224:8000
- 尝试使用域名: http://erode.site:8000

### 2. 邮件未发送
- 检查日志: `journalctl --user -u personalteachers.service -n 100`
- 确认 SMTP 配置正确
- 检查 QQ邮箱授权码是否有效

### 3. 服务未运行
```bash
# 查看服务状态
systemctl --user status personalteachers.service

# 查看错误日志
journalctl --user -u personalteachers.service -n 100 --no-pager
```

---

## 技术支持

如有问题，请查看：
- 服务日志: `journalctl --user -u personalteachers.service -f`
- 应用日志: `tail -f /home/jiqing/PersonalTeachers/backend/storage/logs/app.log`
- API 文档: http://erode.site:8000/docs

---

**部署日期**: 2026-03-01
**部署人**: Claude Code
**版本**: 1.0
