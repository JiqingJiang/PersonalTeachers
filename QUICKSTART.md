# PersonalTeachers 快速访问指南

## 🌐 从您的 macOS 浏览器访问

### 首页 Dashboard
**推荐使用域名（更稳定）：**
```
http://erode.site:8000
```

**或使用公网IP：**
```
http://123.56.81.224:8000
```

---

## 📋 功能页面

| 页面 | URL | 说明 |
|------|-----|------|
| 🏠 首页 | http://erode.site:8000/ | 查看统计信息和服务状态 |
| ⚙️ 偏好设置 | http://erode.site:8000/preferences | 修改推送时间、关键词权重等 |
| 📜 历史语录 | http://erode.site:8000/history | 浏览所有生成的语录 |
| 📖 API文档 | http://erode.site:8000/docs | 查看完整的API文档 |

---

## ⏰ 每日邮件推送

- **当前设置**: 每天 08:25 自动发送
- **收件人**: erode1701@qq.com
- **修改方式**: 访问"偏好设置"页面进行调整

---

## 🔧 服务器管理（SSH 登录后）

### 查看服务状态
```bash
systemctl --user status personalteachers.service
```

### 重启服务
```bash
systemctl --user restart personalteachers.service
```

### 查看实时日志
```bash
journalctl --user -u personalteachers.service -f
```

---

## 📧 测试邮件发送

在服务器上执行：
```bash
curl -X POST http://localhost:8000/api/email/test \
  -H "Content-Type: application/json" \
  -d '{"to_email": "erode1701@qq.com"}'
```

或从 macOS 访问：
```bash
curl -X POST http://erode.site:8000/api/email/test \
  -H "Content-Type: application/json" \
  -d '{"to_email": "erode1701@qq.com"}'
```

---

## 📊 查看统计信息

从 macOS 浏览器访问：
```
http://erode.site:8000/api/stats
```

---

## ❓ 遇到问题？

### 无法访问网站
1. 检查网络连接: `ping erode.site`
2. 确认服务运行: `systemctl --user status personalteachers.service`
3. 查看服务日志: `journalctl --user -u personalteachers.service -n 50`

### 邮件未收到
1. 检查垃圾邮件文件夹
2. 查看服务日志确认邮件发送状态
3. 验证 QQ邮箱 SMTP 配置

---

## 📱 建议收藏

在您的 macOS 浏览器中收藏以下地址：
- **Dashboard**: http://erode.site:8000
- **偏好设置**: http://erode.site:8000/preferences

---

**最后更新**: 2026-03-01
**服务状态**: ✅ 运行中
**公网IP**: 123.56.81.224
**域名**: erode.site
