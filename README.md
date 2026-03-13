# PersonalTeachers - 人生导师每日推送系统

<div align="center">

**通过多元化虚拟导师的每日智慧推送，建立360度认知体系**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [系统架构](#-系统架构) • [文档](#-文档)

</div>

---

## 📖 项目简介

PersonalTeachers是一个**单用户版**的人生智慧推送系统，每天通过邮件向你推送10条来自不同导师的人生建议。

### 核心特点

- 🎭 **50位多元化导师**：历史人物 + 现代人物 + 普通百姓 + 未来的自己
- 🎯 **60个体系化关键词**：覆盖生存/情感/成长/哲思四大维度
- 🤖 **AI多模型生成**：支持 Claude/Gemini/GLM4.7，自动降级容错
- 📧 **每日邮件推送**：定时推送，可自定义时间和权重
- ⚙️ **完全本地化**：数据隐私保护，配置简单，无需服务器

### 适用场景

- 🌅 每日晨间阅读，开启一天
- 📚 建立系统化的认知框架
- 🤔 从多元视角思考人生问题
- 📈 记录和追踪个人成长

---

## ✨ 功能特性

### 智能生成
- ✅ 根据你的偏好动态生成语录
- ✅ 权重调度算法，关注当下最需要的主题
- ✅ 多AI模型支持，自动容错和成本优化
- ✅ 7天内不重复，保持新鲜感

### 多元导师池
| 类别 | 数量 | 代表人物 |
|------|------|----------|
| 历史人物 | 15位 | 老子、孔子、苏格拉底、巴菲特 |
| 现代人物 | 20位 | 马斯克、纳瓦尔、颜宁、吴军 |
| 普通百姓 | 10位 | 打工者、二胎妈妈、退休工人 |
| 未来自己 | 5个模板 | 3年/5年/10年/20年/临终前的你 |

### 60个关键词体系
```
🟢 生存与根基 (15个)：健康、金钱、时间、睡眠...
🔵 关系与情感 (15个)：爱、伴侣、父母、情绪...
🟡 成长与认知 (15个)：选择、认知、执行、复利...
🟣 终极与哲思 (15个)：自由、自我、意义、死亡...
```

### Web管理界面
- 📊 仪表盘：今日语录统计
- ⚙️ 偏好设置：调整关键词权重
- 📚 历史浏览：查看所有历史语录
- 🔧 测试工具：手动生成、测试邮件

---

## 🚀 快速开始

### 环境要求

- Python 3.12+
- 现代浏览器（Chrome/Firefox/Safari）

### 安装步骤

#### 1. 克隆项目

```bash
cd ~/Desktop/Project/vibe-coding/PersonalTeachers
```

#### 2. 创建虚拟环境

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```bash
# 至少配置一个AI模型的API密钥
ANTHROPIC_API_KEY=sk-ant-xxx         # Claude (可选)
GOOGLE_API_KEY=AIzaSyxxx             # Gemini (推荐，免费)
ZHIPUAI_API_KEY=xxx.xxx              # GLM4.7 (可选)

# 配置邮件（用于每日推送）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password      # Gmail需用应用专用密码
```

**获取API密钥**：
- Claude: https://console.anthropic.com/
- Gemini: https://aistudio.google.com/app/apikey (免费)
- GLM4.7: https://open.bigmodel.cn/usercenter/apikeys

**Gmail应用密码设置**：
1. 进入 Google账号设置
2. 安全 → 两步验证
3. 应用专用密码 → 生成新密码

#### 5. 启动服务

```bash
python run.py
```

服务启动后，访问：http://localhost:8000

#### 6. 配置个人信息

编辑 `data/config.yaml`：

```yaml
user:
  name: "你的名字"
  age: 26
  profession: "研究生"
  email: "your-email@example.com"
```

#### 7. 测试生成

1. 打开 http://localhost:8000
2. 点击"立即生成"按钮
3. 等待10条语录生成完成
4. 点击"发送测试邮件"验证邮件功能

---

## 🏗️ 系统架构

```
┌──────────────────┐
│   Web管理界面     │  HTML + TailwindCSS + Alpine.js
└────────┬─────────┘
         │ HTTP API
┌────────▼─────────┐
│   FastAPI应用     │  API + 定时任务 + 邮件
└────────┬─────────┘
         │
┌────────▼─────────┐
│   核心业务逻辑     │  导师池 + 生成引擎 + 权重调度
└────────┬─────────┘
         │
┌────────▼─────────┐
│   AI模型层        │  Claude + Gemini + GLM4.7
└────────┬─────────┘
         │
┌────────▼─────────┐
│   数据存储层       │  SQLite + YAML配置
└──────────────────┘
```

### 技术栈

- **后端**：FastAPI + SQLAlchemy + APScheduler
- **数据库**：SQLite（单文件，无需额外服务）
- **AI模型**：Claude/Gemini/GLM4.7（多模型支持）
- **前端**：HTML + TailwindCSS + Alpine.js（轻量级）
- **邮件**：SMTP标准协议

---

## 📚 文档

- [系统架构设计](docs/architecture.md) - 整体架构和技术选型
- [导师系统设计](docs/mentor_system.md) - 50位导师的分类和数据结构
- [关键词系统设计](docs/keywords_system.md) - 60个关键词的体系说明
- [AI集成文档](docs/ai_integration.md) - AI模型集成和Prompt设计

---

## ⚙️ 配置说明

### 调整关键词权重

编辑 `data/config.yaml`：

```yaml
keyword_weights:
  健康: 2.0      # 高权重 - 更频繁出现
  选择: 2.5      # 最高权重 - 当前最关注
  焦虑: 2.0      # 当前困扰
  金钱: 0.5      # 低权重 - 暂时不关注
```

### 设置推送时间

```yaml
delivery:
  time: "08:00"           # 每日早上8点推送
  enabled: true           # 启用自动推送
```

### 选择AI模型

```yaml
ai_model:
  primary: "auto"         # 自动选择（推荐）
  fallback_order:
    - gemini              # 优先使用免费模型
    - glm                 # 备选低成本模型
    - claude              # 最后的高质量模型
```

---

## 🎯 使用示例

### 场景1：每日晨间阅读

```bash
# 系统每天早上8点自动发送邮件
# 收到邮件后，花10分钟阅读10条语录
# 思考哪几条最有触动，为什么
```

### 场景2：特定困惑期

```yaml
# 当前困惑：职业选择
keyword_weights:
  选择: 3.0      # 大幅提高权重
  焦虑: 2.0
  竞争: 1.5

# 点击"立即生成"，获取10条针对性建议
```

### 场景3：阶段总结

```bash
# 访问 http://localhost:8000/history
# 查看本月所有语录
# 按关键词筛选，发现高频主题
# 反思自己的成长轨迹
```

---

## 💰 成本说明

### AI API成本（每日10条）

| 模型 | 单条成本 | 月成本 |
|------|----------|--------|
| Gemini | 免费 | $0 |
| GLM4.7 | ~¥0.0001 | ~¥0.03 |
| Claude | ~$0.009 | ~$2.7 |

**推荐策略**：
1. 优先使用Gemini（免费额度充足）
2. Gemini失败时切换到GLM4.7（便宜）
3. Claude作为最后备选（高质量）

**估算月成本**：¥0 - ¥30（取决于模型选择）

---

## 🔄 开发路线

### v1.0 (MVP) - 当前版本 ✅
- [x] 50位导师池
- [x] 60个关键词
- [x] AI多模型生成
- [x] 每日邮件推送
- [x] Web管理界面
- [x] 单用户架构

### v1.5 (规划中)
- [ ] 语录质量评分系统
- [ ] 用户反馈收集
- [ ] AI生成结果缓存
- [ ] 更多Prompt优化

### v2.0 (未来)
- [ ] 多用户支持
- [ ] 导师对话模式
- [ ] 语音朗读功能
- [ ] 移动端App

---

## 🤝 贡献指南

这是一个个人项目，但欢迎：
- 🐛 Bug报告
- 💡 功能建议
- 📚 文档改进
- 🎨 Prompt优化

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

灵感来源：
- [FutureMe.org](https://futureme.org/) - 给未来的自己写信
- [Daily Stoic](https://dailystoic.com/) - 每日斯多葛哲学
- [纳瓦尔的智慧推](https://nav.al/) - Nav Ravikant的智慧分享

---

<div align="center">

**愿每日一思，助你成长**

Made with ❤️ by Yourself

</div>
