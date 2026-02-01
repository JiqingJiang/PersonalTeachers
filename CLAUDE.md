# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**PersonalTeachers** 是一个单用户版的人生智慧推送系统，通过50位多元化虚拟导师的每日推送，帮助用户建立360度认知体系。

### 核心技术栈
- **后端**: FastAPI 0.115.0 + Uvicorn
- **数据库**: SQLite (单文件，使用 SQLAlchemy[asyncio] + aiosqlite)
- **AI模型**: 多模型支持 (GLM4.7/DeepSeek/MiniMax/Gemini)，自动降级容错
- **前端**: HTML + TailwindCSS + Alpine.js (纯静态文件，无构建过程)
- **定时任务**: APScheduler
- **邮件**: aiosmtplib (SMTP)

## 常用命令

### 启动服务
```bash
# 从项目根目录
cd backend && python run.py

# 或使用 uvicorn 直接运行
cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 测试
```bash
# 运行所有测试
cd backend && pytest

# 运行特定测试文件
pytest tests/test_ai_models.py

# 运行带标记的测试 (integration 需要 API 密钥)
pytest -m integration

# 带覆盖率报告
pytest --cov=app --cov-report=html
```

### 依赖管理
```bash
# 安装依赖
pip install -r backend/requirements.txt
```

## 架构概览

### 系统分层架构
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
│   AI模型层        │  GLM + DeepSeek + MiniMax + Gemini
└────────┬─────────┘
         │
┌────────▼─────────┐
│   数据存储层       │  SQLite + YAML配置
└──────────────────┘
```

### 核心模块说明

**`backend/app/`** - 应用核心代码
- `main.py` - FastAPI 应用入口，负责生命周期管理（数据库初始化、定时任务启动）
- `api/` - API 路由模块（quotes, mentors, config, email, stats, keywords）
- `ai/` - AI 模型适配器层，统一的 `LLMProvider` 抽象接口
- `models/` - 数据模型（database.py 定义 SQLite 表结构）
- `services/` - 业务服务（email_service.py, scheduler.py）

**`backend/static/`** - 前端静态文件
- `index.html` - 主仪表盘页面
- `preferences.html` - 偏好设置页面
- `history.html` - 历史语录页面

**`backend/data/`** - YAML 配置文件
- `config.yaml` - 用户偏好配置（关键词权重、推送时间、AI模型选择）
- `mentors.yaml` - 50位导师定义（历史人物/现代人物/普通百姓/未来自己）
- `keywords.yaml` - 60个关键词定义（生存/情感/成长/哲思）

**`backend/storage/`** - 运行时数据
- `quotes.db` - SQLite 数据库文件（自动创建）

## AI 模型集成

### 多模型容错机制
系统支持多个 AI 模型，按 `config.yaml` 中 `ai_model.fallback_order` 配置的优先级自动切换。

### LLMProvider 抽象接口
所有 AI 模型都继承自 `app.ai.base.LLMProvider` 抽象基类：

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
```

### 支持的模型类型（`app.ai.base.ModelType`）
- `GLM` - 智谱AI GLM4.7
- `DEEPSEEK` - DeepSeek
- `MINIMAX` - MiniMax
- `GEMINI` - Google Gemini

### 工厂方法
```python
from app.ai import get_llm_provider, ModelType

# 创建 provider 实例
provider = get_llm_provider(ModelType.GLM, api_key="your_api_key")
result = await provider.generate("提示词")
```

## 配置管理

### 环境变量 (`.env`)
必需配置至少一个 AI 模型的 API 密钥：
```bash
# AI 模型 API 密钥（至少配置一个）
ANTHROPIC_API_KEY=sk-ant-xxx         # Claude (可选)
GOOGLE_API_KEY=AIzaSyxxx             # Gemini (推荐，免费)
ZHIPUAI_API_KEY=xxx.xxx              # GLM4.7 (可选)
DEEPSEEK_API_KEY=sk-xxx              # DeepSeek (可选)
MINIMAX_API_KEY=xxx                  # MiniMax (可选)
MINIMAX_GROUP_ID=xxx                 # MiniMax group_id

# 邮件配置（用于每日推送）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### YAML 配置文件
`data/config.yaml` 中的关键配置：
- `keyword_weights` - 关键词权重（影响生成频率）
- `delivery.time` - 每日推送时间
- `delivery.enabled` - 是否启用自动推送
- `ai_model.primary` - 主 AI 模型
- `ai_model.fallback_order` - 备用模型顺序
- `generation.quote_count` - 每次生成的语录数量（默认10条）

## 导师系统

### 50位导师分类
1. **历史人物** (15位) - 老子、孔子、苏格拉底、巴菲特等
2. **现代人物** (20位) - 马斯克、纳瓦尔、颜宁、吴军等
3. **普通百姓** (10位) - 打工者、二胎妈妈、退休工人等
4. **未来自己** (5个模板) - 3年/5年/10年/20年/临终前的你

### 导师数据结构
每个导师在 `data/mentors.yaml` 中定义包含：
- `category` - 导师类别
- `age_range` - 年龄范围
- `keywords` - 相关关键词
- `personality` - 个性特征
- `tone` - 语气风格
- `background` - 背景介绍
- `representative_quotes` - 代表性语录

## 关键词系统

### 60个关键词四大维度
1. **生存与根基** (15个) - 健康、金钱、时间、睡眠等
2. **关系与情感** (15个) - 爱、伴侣、父母、情绪等
3. **成长与认知** (15个) - 选择、认知、执行、复利等
4. **终极与哲思** (15个) - 自由、自我、意义、死亡等

## 开发规范

### 添加新 AI 模型
1. 在 `app/ai/` 下创建新文件（如 `new_provider.py`）
2. 继承 `LLMProvider` 抽象基类
3. 实现 `generate()` 和 `get_model_name()` 方法
4. 在 `app/ai/__init__.py` 中导出
5. 在 `app.ai.base.ModelType` 枚举中添加新类型

### API 路由开发
1. 在 `app/api/` 下创建新模块
2. 使用 `APIRouter()` 创建路由
3. 在 `app/api/__init__.py` 中注册路由

### 测试规范
- 单元测试使用 mock，不调用真实 API
- 集成测试标记 `@pytest.mark.integration`，需要真实 API 密钥
- 异步测试使用 `@pytest.mark.asyncio`