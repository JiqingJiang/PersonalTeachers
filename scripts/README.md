# PersonalTeachers 部署脚本说明

本目录包含 PersonalTeachers 项目的本地部署管理脚本。

## 脚本列表

### 1. start.sh - 服务启动脚本

启动 FastAPI 后台服务和定时任务。

```bash
# 开发模式（前台运行，支持热重载）
./scripts/start.sh

# 生产模式（后台运行）
./scripts/start.sh production
```

**功能：**
- 检查服务是否已在运行
- 激活虚拟环境并检查依赖
- 验证环境变量配置（SMTP、AI 模型）
- 创建必要的目录（storage/logs、storage）
- 启动 uvicorn 服务
- 生产模式记录 PID，后台运行

---

### 2. stop.sh - 服务关闭脚本

安全停止运行中的服务。

```bash
./scripts/stop.sh
```

**功能：**
- 读取 PID 文件或查找运行中的进程
- 发送 TERM 信号优雅关闭（等待最多 10 秒）
- 如进程未响应，使用 KILL 信号强制终止
- 清理 PID 文件和残留进程

---

### 3. status.sh - 服务状态检测脚本

检测服务运行状态、配置有效性、数据库状态。

```bash
# 基本检测
./scripts/status.sh

# 详细输出（包含日志、进程详情）
./scripts/status.sh --verbose
```

**检测项目：**
- **进程状态**: 检查服务进程是否运行
- **网络端口**: 检查 8000 端口是否监听
- **API 健康检查**: 调用 /health 端点
- **环境配置**: 检查 .env 文件和邮件/AI 配置
- **YAML 配置**: 检查 config.yaml（用户邮箱、定时推送）
- **数据库**: 检查数据库文件和语录数量
- **最近日志**: 显示最后 10 行日志

---

## 常见问题排查

### 问题 1: 服务启动后收不到邮件

**排查步骤：**

1. 检查服务状态
   ```bash
   ./scripts/status.sh --verbose
   ```

2. 检查配置
   - 确认 `backend/data/config.yaml` 中 `user.email` 已设置
   - 确认 `delivery.enabled: true`
   - 确认 `delivery.time` 设置正确（格式：HH:MM）

3. 检查邮件配置
   - 确认 `backend/.env` 中 SMTP 配置完整
   - QQ 邮箱：`SMTP_PORT=465`（SSL）或 `587`（STARTTLS）
   - `SMTP_PASSWORD` 使用的是**授权码**，不是 QQ 密码

4. 查看日志
   ```bash
   tail -f backend/storage/logs/server.log
   ```

5. 检查数据库中的邮件发送记录
   ```bash
   sqlite3 backend/storage/quotes.db "SELECT * FROM email_logs ORDER BY sent_at DESC LIMIT 5;"
   ```

### 问题 2: 配置修改后不生效

**原因**: 服务在启动时加载配置，修改配置后需要重启。

**解决方法**:
```bash
./scripts/stop.sh
./scripts/start.sh
```

### 问题 3: 找不到 PID 文件但服务在运行

使用 stop.sh 会自动查找并清理：
```bash
./scripts/stop.sh
```

### 问题 4: 端口 8000 被占用

检查占用进程：
```bash
lsof -i :8000
```

如果需要强制终止：
```bash
kill -9 <PID>
```

---

## 配置说明

### 环境变量 (.env)

```bash
# AI 模型配置（至少配置一个）
ZHIPUAI_API_KEY=xxx       # GLM4.7
DEEPSEEK_API_KEY=xxx      # DeepSeek
GEMINI_API_KEY=xxx        # Gemini（推荐，免费）

# 邮件配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465             # QQ 邮箱使用 465 或 587
SMTP_USERNAME=your@qq.com
SMTP_PASSWORD=授权码       # 不是 QQ 密码
EMAIL_FROM=your@qq.com
```

### YAML 配置 (config.yaml)

```yaml
user:
  email: your@qq.com      # 接收邮件的地址

delivery:
  enabled: true           # 是否启用定时推送
  time: "08:00"           # 推送时间
  timezone: Asia/Shanghai

ai_model:
  primary: glm            # 主 AI 模型
  fallback_order:         # 备用模型顺序
    - glm
    - deepseek
    - gemini
```

---

## 目录结构

```
PersonalTeachers/
├── scripts/
│   ├── start.sh          # 启动脚本
│   ├── stop.sh           # 关闭脚本
│   ├── status.sh         # 状态检测脚本
│   ├── README.md         # 本文档
│   ├── init_db.py        # 数据库初始化
│   ├── test_ai.py        # AI 模型测试
│   └── test_quote_engine.py  # 语录引擎测试
├── backend/
│   ├── app/              # 应用代码
│   ├── data/             # YAML 配置
│   ├── storage/          # 运行时数据
│   │   ├── logs/         # 日志文件
│   │   └── quotes.db     # SQLite 数据库
│   └── .env              # 环境变量
```

---

## 日志位置

- **服务日志**: `backend/storage/logs/server.log`
- **数据库**: `backend/storage/quotes.db`
- **PID 文件**: `backend/app.pid`（运行时生成）
