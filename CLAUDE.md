# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalTeachers v2 — AI 导师语录推送系统。通过多位历史/现代/未来自我的导师视角，结合用户关键词权重偏好，用大模型生成个性化导师语录，定时邮件推送。

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
python run.py              # 启动开发服务器 (uvicorn, port 8000, hot reload)
pip install -r requirements.txt  # 安装依赖
```

### Frontend (Vue 3/Vite, port 5173)
```bash
cd frontend
npm install                # 安装依赖
npm run dev                # 开发服务器
npm run build              # TypeScript 检查 + 生产构建
```

### Admin (Vue 3/Vite, port 5174)
```bash
cd admin
npm install
npm run dev                # 开发服务器 (base: /admin/)
npm run build              # TypeScript 检查 + 生产构建
```

前后端都启动后，Vite dev server 自动将 `/api` 代理到 `http://127.0.0.1:8000`。

## Architecture

三端分离：**frontend**（用户端）+ **admin**（管理后台）+ **backend**（FastAPI REST API）。

### Backend 关键架构

```
backend/app/
├── api/          # 路由层（auth, users, keywords, mentors, preferences, quotes, admin/）
├── models/       # SQLAlchemy 异步模型（User, Mentor, Keyword, AIModel, EmailPool, Quote）
├── core/         # 核心引擎：QuoteEngine, MentorPool, KeywordScheduler, QualityValidator
├── ai/           # LLM 抽象层：base.py(ABC) → openai_adapter.py → FallbackChain
├── services/     # 业务服务：PushScheduler, EmailService, QuoteGenerator, SeedData
├── config.py     # Pydantic Settings，从 .env 加载配置
└── main.py       # FastAPI 应用工厂，lifespan 中初始化 DB + 种子数据 + 调度器
```

- **AI 集成**：`LLMProvider` 抽象基类 → `OpenAICompatibleProvider`（适配所有 OpenAI 兼容 API）→ `FallbackChain`（多模型优先级降级）
- **语录生成流水线**：选关键词（按权重）→ 匹配导师（去重）→ 构建个性化 Prompt → AI 生成（fallback chain）→ 质量校验 → 邮件推送
- **数据库**：aiosqlite 异步 SQLite，`lifespan` 启动时自动建表和填充种子数据
- **定时推送**：APScheduler，时间槽分桶，邮箱池轮换，每日限额

### Frontend 架构

```
frontend/src/
├── api/          # Axios HTTP 客户端，JWT 拦截器自动刷新
├── views/        # 页面组件（Landing, Dashboard, Keywords, Mentors, Settings, History, Auth）
├── stores/       # Pinia store（auth.ts: 用户登录态和 token 管理）
├── router/       # 路由守卫：未登录重定向到 /login
└── components/   # 可复用组件
```

Admin 端结构与 frontend 对称，base path 为 `/admin/`，使用独立 `admin_token` 认证。

### API 结构

- 用户端：`/api/v1/{auth, users, keywords, mentors, preferences, quotes}`
- 管理端：`/api/v1/admin/{users, ai-models, email-pool, stats}`
- 健康检查：`GET /api/v1/health`

## Tech Stack

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 Composition API (`<script setup>`) + TypeScript + Vite + Tailwind CSS v4 + Pinia + Vue Router + Axios |
| 后端 | FastAPI + Uvicorn + SQLAlchemy 2.0 (async) + aiosqlite + Pydantic v2 |
| AI | OpenAI SDK（兼容 DeepSeek/智谱 GLM/Gemini/MiniMax） |
| 认证 | JWT (python-jose + passlib)，localStorage 存储，axios 拦截器自动刷新 |
| 定时任务 | APScheduler |
| 邮件 | aiosmtplib + 邮箱池轮换 |
| 日志 | Loguru |

## Key Design Patterns

- **环境配置**：所有可变配置通过 `backend/.env` 管理（SMTP、JWT secret、admin 凭证等），`config.py` 用 Pydantic Settings 加载
- **种子数据**：`services/seed.py` 启动时初始化 60 个系统关键词（四象限）和预设导师，数据库迁移通过 `init_db()` 处理
- **双 Prompt 模板**：普通导师和 future_self 导师使用不同的 prompt 策略
- **个人化权重**：用户对关键词和导师各有独立权重，影响生成内容和推送频率

## Git Branch Strategy

- `main` — 生产分支，通过 PR 合入，push 触发自动部署
- `develop` — 日常开发分支
- `feature/*` — 功能分支，从 develop 分出，PR 回 develop
- `hotfix/*` — 紧急修复，从 main 分出

日常开发在 develop 上，发布时 PR 合到 main。

## Deployment

- **自动部署**：push to main → GitHub Actions 构建 + rsync 到阿里云 ECS + 重启服务
- **手动构建**：`cd frontend && npm run build`，`cd admin && npm run build`