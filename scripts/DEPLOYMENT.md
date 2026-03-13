# PersonalTeachers 稳定部署指南

本指南说明如何在 macOS 上配置 PersonalTeachers 服务，使其在网络切换、代理变化等场景下保持稳定运行。

## 📋 目录

1. [方案概述](#方案概述)
2. [快速开始](#快速开始)
3. [launchd 自动启动](#launchd-自动启动)
4. [看门狗监控](#看门狗监控)
5. [代理配置](#代理配置)
6. [故障排查](#故障排查)

---

## 方案概述

### 稳定性方案

| 组件 | 功能 | 说明 |
|------|------|------|
| **launchd** | 系统级服务管理 | 开机自启动、崩溃自动重启、网络变化时重启 |
| **watchdog** | 看门狗监控 | 定期健康检查、连续失败自动恢复、网络切换检测 |
| **proxy.sh** | 代理管理 | 自动/手动配置代理、一键切换 |

### 工作流程

```
┌─────────────────────────────────────────────────────────┐
│                    macOS 系统                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │              launchd (系统级)                      │  │
│  │  • 开机启动                                        │  │
│  │  • 崩溃重启                                        │  │
│  │  • 网络变化检测                                    │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │            PersonalTeachers 服务                   │  │
│  │  • FastAPI Web 服务                                │  │
│  │  • 定时推送任务                                     │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↑                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │              watchdog (看门狗)                     │  │
│  │  • 每 60 秒健康检查                                │  │
│  │  • 网络变化检测                                    │  │
│  │  • 连续 3 次失败自动重启                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 快速开始

### 1. 基础启动（手动）

```bash
# 启动服务
./scripts/start.sh production

# 查看状态
./scripts/status.sh

# 停止服务
./scripts/stop.sh
```

### 2. 配置代理（如需要）

```bash
# 自动检测系统代理
./scripts/proxy.sh auto

# 或手动设置
./scripts/proxy.sh set

# 查看代理状态
./scripts/proxy.sh status
```

### 3. 启动看门狗监控

```bash
# 后台运行看门狗
./scripts/watchdog.sh --daemon

# 查看看门狗日志
tail -f backend/storage/logs/watchdog.log
```

---

## launchd 自动启动

使用 launchd 配置开机自启动和崩溃自动重启。

### 安装 launchd 服务

```bash
# 1. 复制 plist 文件到 LaunchAgents 目录
cp scripts/com.personalteachers.agent.plist ~/Library/LaunchAgents/

# 2. 修改 plist 文件中的路径（将 /Users/jiqing 替换为你的实际路径）
sed -i '' "s|/Users/jiqing|$HOME|g" ~/Library/LaunchAgents/com.personalteachers.agent.plist

# 3. 加载服务
launchctl load ~/Library/LaunchAgents/com.personalteachers.agent.plist

# 4. 启动服务
launchctl start com.personalteachers.agent
```

### 管理 launchd 服务

```bash
# 查看服务状态
launchctl list | grep personalteachers

# 停止服务
launchctl stop com.personalteachers.agent

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.personalteachers.agent.plist

# 查看服务日志
tail -f ~/Library/Logs/com.personalteachers.agent.log
```

### launchd 配置说明

plist 文件中的关键配置：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `RunAtLoad` | true | 加载时立即启动 |
| `KeepAlive` | true | 进程退出时自动重启 |
| `ThrottleInterval` | 10 | 重启间隔至少 10 秒 |
| `WatchPaths` | 网络配置 | 网络变化时触发重启 |
| `StartInterval` | 3600 | 每小时检查一次 |

---

## 看门狗监控

看门狗脚本提供更细粒度的监控和恢复机制。

### 启动看门狗

```bash
# 后台模式（推荐）
./scripts/watchdog.sh --daemon

# 前台模式（调试用）
./scripts/watchdog.sh
```

### 看门狗功能

1. **健康检查**：每 60 秒检查一次
   - 进程是否运行
   - 端口 8000 是否监听
   - HTTP 健康端点是否正常

2. **网络变化检测**
   - 检测 WiFi 切换
   - 检测 IP 地址变化
   - 自动检测系统代理设置

3. **自动恢复**
   - 连续 3 次健康检查失败自动重启
   - 网络变化后自动检测并应用代理
   - 重启失败后记录日志

4. **日志记录**
   ```
   [2025-01-23 10:30:00] [INFO] 🐕 PersonalTeachers 看门狗启动
   [2025-01-23 10:30:01] [INFO] ✅ 服务启动成功
   [2025-01-23 10:31:00] [INFO] 🌐 网络变化检测: WiFi: Home_WiFi | IP: 192.168.1.100
   [2025-01-23 10:35:00] [WARN] ⚠️  外网连接不可用
   [2025-01-23 10:36:00] [INFO] 🌐 网络变化检测: WiFi: Office_WiFi | IP: 10.0.0.50
   [2025-01-23 10:36:01] [INFO] 🌐 检测到系统代理: 127.0.0.1:7890
   [2025-01-23 10:36:05] [INFO] ✅ 健康检查通过
   ```

### 停止看门狗

```bash
# 查看待门狗进程
cat backend/watchdog.pid

# 停止看门狗
kill $(cat backend/watchdog.pid)
```

---

## 代理配置

当网络需要代理时，使用 proxy.sh 脚本管理。

### 查看代理状态

```bash
./scripts/proxy.sh status
```

输出示例：
```
════════════════════════════════════════════════════════
📊 代理状态
════════════════════════════════════════════════════════

系统代理设置:
  HTTP 代理: 未启用
  HTTPS 代理: 未启用

当前环境变量:
  HTTP_PROXY: 未设置
  HTTPS_PROXY: 未设置

项目 .env 配置:
  http_proxy: 未配置
  https_proxy: 未配置

连接测试:
  ❌ 外网连接失败
```

### 自动检测系统代理

```bash
./scripts/proxy.sh auto
```

如果系统已配置代理（如 Clash、V2Ray 等），脚本会自动检测并应用。

### 手动设置代理

```bash
./scripts/proxy.sh set
```

常用代理端口：
- Clash: `127.0.0.1:7890`
- V2Ray: `127.0.0.1:10809`
- Shadowsocks: `127.0.0.1:1080`

### 取消代理

```bash
./scripts/proxy.sh unset
```

---

## 故障排查

### 问题 1: 服务频繁重启

**现象**: 日志显示服务反复启动和退出

**排查**:
```bash
# 查看服务日志
tail -50 backend/storage/logs/server.log

# 查看启动错误
./scripts/start.sh production
```

**常见原因**:
- 端口 8000 被占用
- Python 依赖缺失
- 环境变量配置错误

### 问题 2: 网络切换后服务失效

**现象**: 切换 WiFi 后服务无法访问外部 API

**排查**:
```bash
# 检查网络状态
./scripts/status.sh --verbose

# 测试代理
./scripts/proxy.sh status
```

**解决方法**:
1. 如果需要代理，运行 `./scripts/proxy.sh auto`
2. 重启服务: `./scripts/stop.sh && ./scripts/start.sh production`

### 问题 3: 看门狗误判重启

**现象**: 服务正常运行但被看门狗重启

**排查**:
```bash
# 查看看门狗日志
tail -50 backend/storage/logs/watchdog.log
```

**解决方法**:
- 增加健康检查失败阈值（修改 `max_network_failures`）
- 增加检查间隔（修改 `CHECK_INTERVAL`）

### 问题 4: launchd 服务无法启动

**现象**: `launchctl start` 报错

**排查**:
```bash
# 检查 plist 语法
plutil -lint ~/Library/LaunchAgents/com.personalteachers.agent.plist

# 查看系统日志
log show --predicate 'process == "PersonalTeachers"' --last 1m
```

**解决方法**:
- 确保 plist 文件中的路径正确
- 检查文件权限: `chmod 644 ~/Library/LaunchAgents/com.personalteachers.agent.plist`

---

## 推荐配置

### 日常使用（推荐）

```bash
# 1. 安装 launchd 服务（开机自启动）
cp scripts/com.personalteachers.agent.plist ~/Library/LaunchAgents/
sed -i '' "s|/Users/jiqing|$HOME|g" ~/Library/LaunchAgents/com.personalteachers.agent.plist
launchctl load ~/Library/LaunchAgents/com.personalteachers.agent.plist

# 2. 启动看门狗监控（更细粒度的恢复）
./scripts/watchdog.sh --daemon
```

### 开发调试

```bash
# 前台运行，方便查看日志
./scripts/start.sh

# 或使用开发模式（支持热重载）
./scripts/start.sh development
```

### 代理环境

```bash
# 1. 配置系统代理（Clash/V2Ray）
# 2. 应用代理到项目
./scripts/proxy.sh auto

# 3. 启动服务
./scripts/start.sh production

# 4. 启动看门狗
./scripts/watchdog.sh --daemon
```

---

## 日志位置

| 日志类型 | 路径 |
|----------|------|
| 服务日志 | `backend/storage/logs/server.log` |
| 看门狗日志 | `backend/storage/logs/watchdog.log` |
| launchd 日志 | `backend/storage/logs/launchd.stdout.log` |

---

## 脚本清单

| 脚本 | 功能 |
|------|------|
| `start.sh` | 启动服务 |
| `stop.sh` | 停止服务 |
| `status.sh` | 查看状态 |
| `watchdog.sh` | 看门狗监控 |
| `proxy.sh` | 代理配置 |
| `com.personalteachers.agent.plist` | launchd 配置 |