# 阿里云服务器部署指南

> **首次部署**：参考本文档完成服务器初始化。后续更新通过 GitHub Actions 自动部署，无需手动操作。
>
> **手动部署（应急）**：在本地项目根目录执行 `./scripts/deploy.sh`。
>
> **自动部署流程**：代码合并到 main 分支 → GitHub Actions 自动构建并部署到服务器。

## 1. 服务器环境检查

### 1.1 检查操作系统版本
```bash
cat /etc/os-release
```
输出示例：
- CentOS: `ID="centos"` 或 `ID="rhel"`
- Ubuntu: `ID="ubuntu"`
- Debian: `ID="debian"`

### 1.2 检查 Python 版本
```bash
python3 --version
```
需要 Python 3.11 或更高版本。如果版本过低，需要升级：

**CentOS 7/8 升级 Python:**
```bash
# 安装依赖
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel

# 下载并编译 Python 3.11
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
tar -xzf Python-3.11.0.tgz
cd Python-3.11.0
./configure --enable-optimizations
make altinstall
```

**Ubuntu/Debian 升级 Python:**
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

---

## 2. 项目上传到服务器

### 方式A: 使用 SCP 上传（推荐）
```bash
# 在本地执行，将整个项目上传到服务器
scp -r /Users/jiqing/Desktop/Project/vibe-coding/PersonalTeachers/backend root@your-server-ip:/root/

# 或如果使用密钥登录
scp -i /path/to/key -r /Users/jiqing/Desktop/Project/vibe-coding/PersonalTeachers/backend root@your-server-ip:/root/
```

### 方式B: 使用 Git 克隆
```bash
# 在服务器上执行
cd /root
git clone <your-repo-url>
cd PersonalTeachers/backend
```

### 方式C: 使用 FTP 工具
- 使用 FileZilla 或 WinSCP 等工具
- 直接拖拽 backend 文件夹到服务器

---

## 3. 安装项目依赖

### 3.1 进入项目目录
```bash
cd /root/backend
```

### 3.2 创建虚拟环境
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 3.3 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**如果安装失败（某些包需要编译）:**
```bash
# CentOS
sudo yum install -y python3-devel gcc

# Ubuntu/Debian
sudo apt install -y python3-dev build-essential
```

---

## 4. 配置生产环境

### 4.1 复制环境变量配置
```bash
cp .env.example .env
vim .env
```

**必须修改的配置:**
```bash
# 邮件配置（必须配置）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your-email@qq.com
SMTP_PASSWORD=your-authorization-code
EMAIL_FROM=your-email@qq.com

# AI 模型配置（至少配置一个）
ZHIPUAI_API_KEY=your-glm-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
MINIMAX_API_KEY=your-minimax-api-key

# 生产模式配置
DEBUG=false
HOST=0.0.0.0    # 监听所有网络接口
PORT=8000
```

### 4.2 修改用户配置
```bash
vim data/config.yaml
```
确认以下配置正确：
```yaml
user:
  name: "你的名字"
  age: 26
  email: "your-email@qq.com"    # 修改为你的邮箱

delivery:
  enabled: true
  time: '08:00'                 # 每日推送时间
  timezone: Asia/Shanghai
```

### 4.3 创建必要的目录
```bash
mkdir -p storage/logs
mkdir -p storage/backups
```

---

## 5. 配置系统服务（Systemd）

创建 systemd 服务文件，实现开机自启和崩溃自动重启：
```bash
sudo vim /etc/systemd/system/personalteachers.service
```

**服务配置内容:**
```ini
[Unit]
Description=PersonalTeachers - 人生导师每日推送系统
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/backend
Environment="PATH=/root/backend/venv/bin"
ExecStart=/root/backend/venv/bin/python run.py
Restart=always
RestartSec=10

# 日志配置
StandardOutput=append:/root/backend/storage/logs/service.log
StandardError=append:/root/backend/storage/logs/service_error.log

[Install]
WantedBy=multi-user.target
```

**启用并启动服务:**
```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable personalteachers

# 启动服务
sudo systemctl start personalteachers

# 查看服务状态
sudo systemctl status personalteachers

# 查看日志
sudo journalctl -u personalteachers -f
```

**服务管理命令:**
```bash
# 停止服务
sudo systemctl stop personalteachers

# 重启服务
sudo systemctl restart personalteachers

# 查看最近100条日志
sudo journalctl -u personalteachers -n 100
```

---

## 6. 配置防火墙

### 6.1 开放端口 8000
**CentOS (firewalld):**
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

**Ubuntu (ufw):**
```bash
sudo ufw allow 8000/tcp
sudo ufw status
```

### 6.2 阿里云安全组配置
1. 登录阿里云控制台
2. 进入 **云服务器 ECS** → **安全组**
3. 点击 **配置规则** → **添加安全组规则**
4. 配置:
   - 端口范围: `8000/8000`
   - 授权对象: `0.0.0.0/0`
   - 协议类型: `TCP`

---

## 7. 域名配置（可选）

### 7.1 解析域名到服务器IP
在域名服务商（阿里云/腾讯云等）添加 A 记录：
```
记录类型: A
主机记录: @ 或 www
记录值: 你的服务器公网IP
TTL: 600
```

### 7.2 访问测试
```bash
# 使用 IP 访问
curl http://your-server-ip:8000

# 使用域名访问（如果已配置）
curl http://your-domain.com
```

---

## 8. 验证部署

### 8.1 检查服务状态
```bash
# 查看服务是否运行
sudo systemctl status personalteachers

# 应该看到 "active (running)" 状态
```

### 8.2 测试 Web 界面
在浏览器访问：
- `http://your-server-ip:8000`
- `http://your-domain.com`（如果配置了域名）

应该看到主页仪表盘。

### 8.3 测试邮件发送
1. 进入 Web 界面
2. 点击 **测试邮件** 按钮
3. 检查邮箱是否收到测试邮件

### 8.4 测试语录生成
1. 点击 **立即生成** 按钮
2. 查看是否成功生成 10 条语录

---

## 9. 常用维护命令

### 查看日志
```bash
# 实时查看应用日志
tail -f /root/backend/storage/logs/app.log

# 查看 systemd 服务日志
sudo journalctl -u personalteachers -f

# 查看错误日志
tail -f /root/backend/storage/logs/service_error.log
```

### 备份数据
```bash
# 备份数据库
cp /root/backend/storage/quotes.db /root/backend/storage/backups/quotes_$(date +%Y%m%d).db

# 备份配置
tar -czf /root/backend/storage/backups/config_$(date +%Y%m%d).tar.gz /root/backend/data /root/backend/.env
```

### 更新代码
```bash
# 停止服务
sudo systemctl stop personalteachers

# 拉取最新代码
cd /root/backend
git pull

# 或手动上传新文件后解压

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl start personalteachers
```

---

## 10. 故障排查

### 问题1: 服务无法启动
```bash
# 查看详细错误日志
sudo journalctl -u personalteachers -n 50 --no-pager

# 常见原因：
# - Python 路径错误 → 检查 which python3.11
# - 端口被占用 → lsof -i:8000
# - 虚拟环境未激活 → source venv/bin/activate
```

### 问题2: 无法访问 Web 界面
```bash
# 检查端口监听
netstat -tulnp | grep 8000

# 检查防火墙
sudo firewall-cmd --list-ports

# 检查阿里云安全组
# 在控制台确认 8000 端口已开放
```

### 问题3: 邮件发送失败
```bash
# 检查 .env 配置
cat .env | grep SMTP

# 测试邮件发送
python scripts/send_test_email.py
```

### 问题4: AI 生成失败
```bash
# 检查 API 密钥
cat .env | grep API_KEY

# 测试 AI 连接
python scripts/test_ai.py
```

---

## 11. 监控与告警（可选）

### 简单监控脚本
创建 `/root/backend/scripts/monitor.sh`:
```bash
#!/bin/bash
# 检查服务状态
if ! systemctl is-active --quiet personalteachers; then
    echo "[$(date)] Service is down, restarting..." >> /root/backend/storage/logs/monitor.log
    systemctl restart personalteachers
fi

# 检查磁盘空间
DISK_USAGE=$(df /root | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$(date)] Disk usage: ${DISK_USAGE}%" >> /root/backend/storage/logs/monitor.log
fi
```

添加到 crontab:
```bash
crontab -e
# 添加：每 5 分钟检查一次
*/5 * * * * /root/backend/scripts/monitor.sh
```

---

## 12. HTTPS 配置（未来升级）

当需要配置 HTTPS 时，使用 Certbot + Let's Encrypt:

### 安装 Certbot
```bash
# CentOS
sudo yum install -y certbot python3-certbot-nginx

# Ubuntu
sudo apt install -y certbot python3-certbot-nginx
```

### 申请证书
```bash
sudo certbot --nginx -d your-domain.com
```

### 自动续期
```bash
# 测试续期
sudo certbot renew --dry-run

# crontab 自动续期（已自动配置）
crontab -l | grep certbot
```

---

## 13. 快速部署清单

- [ ] 1. 检查操作系统版本
- [ ] 2. 检查/安装 Python 3.11+
- [ ] 3. 上传项目到服务器
- [ ] 4. 创建虚拟环境
- [ ] 5. 安装依赖
- [ ] 6. 配置 .env 文件
- [ ] 7. 修改 config.yaml
- [ ] 8. 创建 systemd 服务
- [ ] 9. 开启防火墙端口
- [ ] 10. 配置阿里云安全组
- [ ] 11. 启动服务
- [ ] 12. 测试 Web 访问
- [ ] 13. 测试邮件发送
- [ ] 14. 测试语录生成
- [ ] 15. 配置域名解析（可选）
- [ ] 16. 设置监控脚本（可选）

---

## 14. 联系与支持

如遇到问题：
1. 查看日志: `tail -f storage/logs/app.log`
2. 检查服务状态: `sudo systemctl status personalteachers`
3. 查看本文档的故障排查部分
