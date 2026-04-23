# PersonalTeachers v2

> AI 驱动的个性化导师语录推送系统 — 每天一封来自人生导师的信

通过 58 位跨越时代与阶层的虚拟导师（历史哲人、现代精英、普通百姓、未来自己），结合 60 个人生关键词和你的个人背景，用大模型生成专属导师语录，每日定时邮件推送。

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

## 特性

- **58 位导师池** — 历史人物、现代精英、普通百姓、未来自己四个类别
- **60 个人生关键词** — 四象限体系：生存根基、关系情感、成长认知、终极哲思
- **AI 个性化生成** — 结合用户背景、偏好权重、关键词匹配，定制化语录
- **多模型降级** — 支持 DeepSeek、智谱 GLM 等任意 OpenAI 兼容接口，自动故障切换
- **定时邮件推送** — 时间槽分桶调度，多邮箱池轮换，智能限额
- **完整管理后台** — 用户管理、AI 模型配置、邮箱池、推送监控

## 技术栈

| 层       | 技术                                                   |
| -------- | ------------------------------------------------------ |
| 用户前端 | Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia       |
| 管理后台 | Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia       |
| 后端 API | FastAPI + Uvicorn + SQLAlchemy 2.0 (async) + aiosqlite |
| AI 集成  | OpenAI 兼容接口（DeepSeek / 智谱 GLM / 自定义）        |
| 认证     | JWT (access token + refresh token)                     |
| 定时任务 | APScheduler                                            |
| 邮件     | aiosmtplib + 多邮箱池轮换                              |
| 部署     | GitHub Actions + rsync + systemd                       |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 克隆项目

```bash
git clone https://github.com/JiqingJiang/PersonalTeachers.git
cd PersonalTeachers
```

### 2. 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.development .env
# 编辑 .env 填入你的配置（开发环境使用默认值即可启动）
```

**至少需要配置一个 AI 模型的 API Key 才能使用语录生成功能。** 进入管理后台 `/admin` 在 AI 模型管理页面配置。

### 3. 前端

```bash
# 用户端
cd frontend
npm install
npm run dev      # http://localhost:5173

# 管理后台（新终端）
cd admin
npm install
npm run dev      # http://localhost:5174
```

### 4. 启动

```bash
cd backend
python run.py    # http://localhost:8000
```

前后端都启动后，访问 `http://localhost:5173` 即可使用。

## 环境配置

项目通过 `.env` 文件管理配置，支持开发/生产环境分离：

| 文件                 | 用途                             | 是否提交 Git |
| -------------------- | -------------------------------- | :----------: |
| `.env.development` | 开发环境默认配置                 |      ✅      |
| `.env.production`  | 生产环境配置模板（占位符）       |      ✅      |
| `.env`             | 实际运行配置（从模板复制并填写） |      ❌      |

主要配置项：

```bash
# AI 模型（至少配置一个，也可在管理后台配置）
DEEPSEEK_API_KEY=your-key
ZHIPUAI_API_KEY=your-key

# 邮件推送（也可在管理后台邮箱池配置）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USERNAME=your-email@qq.com
SMTP_PASSWORD=your-auth-code

# 管理员（首次启动自动创建）
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-password
```

## 项目结构

```
├── frontend/           # 用户端 Vue 3 应用
│   └── src/
│       ├── api/        # Axios HTTP 客户端
│       ├── views/      # 页面组件
│       ├── stores/     # Pinia 状态管理
│       └── router/     # 路由配置
├── admin/              # 管理后台 Vue 3 应用
│   └── src/
│       └── views/      # 管理页面（用户/模型/邮箱/统计）
├── backend/            # FastAPI 后端
│   └── app/
│       ├── api/        # REST API 路由
│       ├── models/     # SQLAlchemy 数据模型
│       ├── core/       # 核心引擎（语录生成/导师匹配/调度）
│       ├── ai/         # LLM 抽象层（Provider + Fallback Chain）
│       ├── services/   # 业务服务（推送/邮件/种子数据）
│       ├── config.py   # 环境配置
│       └── main.py     # 应用入口
└── .github/workflows/  # GitHub Actions CI/CD
```

## 部署

项目使用 GitHub Actions 自动部署。推送代码到 `main` 分支后自动构建并部署到服务器。

详细部署指南见 [backend/docs/deployment.md](backend/docs/deployment.md)。

## 导师体系

| 类别     | 数量 | 示例                                     |
| -------- | :--: | ---------------------------------------- |
| 历史人物 |  22  | 老子、孔子、苏格拉底、苏轼、曾国藩       |
| 现代精英 |  23  | 埃隆·马斯克、纳瓦尔、张一鸣、万维钢     |
| 普通百姓 |  10  | 大厂程序员、二胎妈妈、小店主、高三班主任 |
| 未来自己 |  5  | 3年后的你、10年后的你、临终前的你        |

## 关键词四象限

- **生存根基** — 健康、金钱、时间、睡眠、安全感...
- **关系情感** — 爱、父母、伴侣、孤独、信任、遗憾...
- **成长认知** — 选择、认知、习惯、复利、专注、执行...
- **终极哲思** — 自由、意义、死亡、命运、真理、无常...

## License

[Apache License 2.0](LICENSE)
