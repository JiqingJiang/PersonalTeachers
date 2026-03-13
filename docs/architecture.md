# PersonalTeachers 系统架构设计

## 📖 文档概述

**为什么需要这个文档？**
- 明确系统整体架构和技术选型
- 为后续开发提供统一的设计规范
- 方便团队协作和知识传承

**适合谁阅读？**
- 项目开发者（理解系统全貌）
- 自己未来回顾（快速恢复上下文）

---

## 🎯 设计哲学

### 核心理念
> 通过**多元化虚拟导师**的每日智慧推送，帮助建立**360度认知体系**

### 关键设计决策

#### 1. 单用户架构（vs 多用户SaaS）

**为什么选择单用户？**
- ✅ **简化复杂度**：无需注册/登录/权限系统
- ✅ **降低成本**：无服务器费用，本地运行即可
- ✅ **快速迭代**：专注核心功能，快速验证价值
- ✅ **隐私保护**：数据完全本地化

**未来扩展路径**：
- v2.0：添加多用户支持（若需要分享给朋友）
- v3.0：SaaS化部署（若需要商业运营）

#### 2. AI多模型集成（vs 单一模型）

**为什么支持多模型？**
- ✅ **成本优化**：Gemini免费额度优先，GLM4.7低成本备份
- ✅ **质量保障**：Claude作为高质量备选
- ✅ **风格多样**：不同模型有不同的生成风格
- ✅ **容错能力**：主模型失败时自动切换

**模型优先级策略**：
```
1. Gemini (免费) → 2. GLM4.7 (便宜) → 3. Claude (高质量)
```

#### 3. YAML配置驱动（vs 数据库存储）

**为什么使用YAML？**
- ✅ **可读性强**：人类友好，易于手动编辑
- ✅ **版本控制**：Git友好，变更可追踪
- ✅ **灵活性高**：修改配置无需数据库迁移
- ✅ **备份方便**：文件系统级别备份即可

**配置文件分类**：
- `config.yaml` - 用户偏好（频繁修改）
- `mentors.yaml` - 导师池定义（低频修改）
- `keywords.yaml` - 关键词定义（几乎不变）

#### 4. 轻量级定时任务（vs Celery+Redis）

**为什么选择APScheduler？**
- ✅ **零依赖**：无需Redis等外部服务
- ✅ **简单直观**：单进程内调度，代码简洁
- ✅ **满足需求**：单用户场景下性能足够
- ✅ **易维护**：不增加系统复杂度

**适用场景**：
- ✅ 每日定时推送
- ✅ 周期性任务（如每周生成总结）
- ❌ 高并发分布式任务（未来升级到Celery）

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Web管理界面 (Browser)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 偏好设置      │  │ 历史语录      │  │  手动生成    │       │
│  │ (YAML编辑)    │  │ (浏览/搜索)   │  │  (测试按钮)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP (REST API)
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI 应用 (单进程)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  API路由     │  │  定时任务     │  │  邮件发送    │       │
│  │  (8个端点)   │  │  (APScheduler)│  │  (smtplib)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      核心业务逻辑层                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ 导师池管理    │  │ 语录生成引擎  │  │  权重调度    │       │
│  │ (50位导师)   │  │ (多模型LLM)   │  │ (60关键词)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据存储层 (本地)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   SQLite     │  │ YAML配置文件  │  │  文件日志     │       │
│  │ (语录历史)   │  │ (导师/偏好)   │  │  (运行记录)   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      外部服务 (AI APIs)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Claude     │  │   Gemini     │  │    GLM4.7    │       │
│  │   API        │  │     API      │  │     API      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 数据流图

#### 语录生成流程

```
用户触发 (Web/定时)
    ↓
读取配置 (config.yaml)
    ↓
权重调度器选择10个关键词
    ↓
导师池匹配 (根据关键词+偏好)
    ↓
AI模型调用 (Claude/Gemini/GLM4.7)
    ↓
质量过滤 (去重、长度检查)
    ↓
保存到SQLite
    ↓
返回给用户 / 发送邮件
```

#### 邮件推送流程

```
APScheduler触发 (每日8:00)
    ↓
读取用户配置
    ↓
调用语录生成引擎
    ↓
渲染邮件模板 (HTML)
    ↓
发送邮件 (aiosmtplib)
    ↓
记录发送日志
    ↓
保存语录到数据库
```

---

## 📦 模块设计

### 1. API层 (`app/api/`)

**职责**：处理HTTP请求，参数校验，返回响应

**端点列表**：
```
POST   /api/quotes/generate      # 手动生成语录
GET    /api/quotes/history       # 历史语录查询
GET    /api/quotes/{id}          # 单条语录详情

GET    /api/mentors              # 导师列表
GET    /api/mentors/{id}         # 导师详情

GET    /api/keywords             # 关键词列表
GET    /api/config               # 读取配置
PUT    /api/config               # 更新配置

POST   /api/email/test           # 测试邮件
GET    /api/email/logs           # 邮件日志

GET    /api/stats                # 统计信息
```

### 2. 核心业务逻辑层 (`app/core/`)

#### 2.1 导师池管理 (`mentor_pool.py`)

**数据结构**：
```python
@dataclass
class Mentor:
    id: str
    name: str
    category: MentorCategory  # HISTORICAL/MODERN/FUTURE_SELF/COMMON
    age_range: tuple[int, int]
    field: str
    perspective: Perspective  # TOP/BOTTOM/EMOTIONAL/RATIONAL
    keywords: list[str]
    personality: str
    tone: str
    background: str
```

**核心方法**：
- `get_mentors_by_keyword(keyword: str) -> List[Mentor]`
- `get_mentors_by_category(category: MentorCategory) -> List[Mentor]`
- `get_random_mentor(category: MentorCategory, age: int) -> Mentor`

#### 2.2 权重调度器 (`weight_scheduler.py`)

**算法**：
```
1. 读取用户配置的 keyword_weights
2. 计算每个关键词的选中概率：P(kw) = weight(kw) / sum(weights)
3. 使用轮盘赌算法选择10个关键词
4. 确保多样性：同一象限最多5条
```

**核心方法**：
- `select_keywords(count: int, weights: dict) -> List[str]`

#### 2.3 语录生成引擎 (`quote_engine.py`)

**生成流程**：
```
1. 权重调度器选择10个关键词
2. 为每个关键词匹配合适的导师
3. 构建Prompt（包含导师人设）
4. 调用AI模型生成
5. 质量过滤（去重、长度、敏感词）
6. 失败重试（最多3次，切换模型）
```

**核心方法**：
- `generate_quotes(count: int, config: Config) -> List[Quote]`

#### 2.4 未来自己生成器 (`future_self.py`)

**特殊逻辑**：
```
1. 分析当前用户状态（年龄、职业、困惑）
2. 动态生成未来自己的人设（+10岁）
3. 基于当前困惑点生成建议
4. 语气更加温暖、理解、鼓励
```

**核心方法**：
- `generate_future_self_quote(keyword: str, user_state: dict) -> Quote`

### 3. AI集成层 (`app/ai/`)

#### 3.1 统一接口 (`base.py`)

**抽象基类**：
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
```

**模型工厂**：
```python
def get_llm_provider(model_name: str) -> LLMProvider:
    match model_name:
        case "claude":
            return ClaudeProvider()
        case "gemini":
            return GeminiProvider()
        case "glm":
            return GLMProvider()
        case _:
            raise ValueError(f"Unknown model: {model_name}")
```

#### 3.2 Prompt模板管理

**普通导师Prompt**：
```
你是{mentor_name}，{age}岁的{field}专家。
你的性格特点：{personality}
你的说话风格：{tone}
你的背景经历：{background}

现在请针对【{keyword}】这个主题，给一位{user_age}岁的{user_profession}一条简短的人生建议。
要求：
1. 100-150字中文
2. 符合你的人设和视角
3. 有具体的场景或例子
4. 不是空洞的鸡汤，而是可执行的经验
```

**未来自己Prompt**：
```
你是10年后的自己（{future_age}岁），现在的你正面临{current_challenge}。
作为未来的你，请基于以下信息给现在的自己一些建议：
- 当前状态：{current_status}
- 困惑点：{confusion}
- 期望方向：{expectation}

请以温暖、理解的语气，分享你从现在到{future_age}岁期间关于【{keyword}】的心得体会。
```

### 4. 服务层 (`app/services/`)

#### 4.1 邮件服务 (`email_service.py`)

**功能**：
- 异步发送邮件（aiosmtplib）
- 支持HTML模板渲染
- 发送失败重试机制
- 发送日志记录

**核心方法**：
```python
async def send_email(
    to: str,
    subject: str,
    html: str,
    max_retries: int = 3
) -> bool
```

#### 4.2 定时任务 (`scheduler.py`)

**功能**：
- 使用APScheduler管理定时任务
- 每日8:00自动推送语录
- 支持动态修改调度时间

**任务定义**：
```python
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=config['delivery']['hour'],
                         minute=config['delivery']['minute'])
async def daily_quote_delivery():
    # ... 推送逻辑
```

### 5. 数据模型层 (`app/models/`)

#### 5.1 数据库模型 (SQLAlchemy)

```python
class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    mentor_name = Column(String)
    mentor_category = Column(String)
    keyword = Column(String)
    content = Column(Text)
    ai_model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Quote {self.mentor_name} - {self.keyword}>"
```

#### 5.2 Pydantic模型 (API验证)

```python
class QuoteResponse(BaseModel):
    id: int
    mentor_name: str
    mentor_category: str
    keyword: str
    content: str
    created_at: datetime

class ConfigUpdate(BaseModel):
    keyword_weights: Optional[Dict[str, float]] = None
    delivery_time: Optional[str] = None
    ai_model: Optional[str] = None
```

---

## 🗄️ 数据存储设计

### SQLite数据库 (`storage/quotes.db`)

**表结构**：

```sql
-- 语录表
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mentor_name TEXT NOT NULL,
    mentor_category TEXT NOT NULL,
    mentor_age INTEGER,
    keyword TEXT NOT NULL,
    content TEXT NOT NULL,
    ai_model TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_created_at (created_at)
);

-- 邮件发送日志表
CREATE TABLE email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    INDEX idx_sent_at (sent_at)
);
```

### YAML配置文件

#### `data/config.yaml` (用户配置)

```yaml
# 用户基本信息
user:
  name: "你的名字"
  age: 26
  profession: "研究生"
  email: "your-email@example.com"

# 推送设置
delivery:
  time: "08:00"
  timezone: "Asia/Shanghai"
  enabled: true

# 关键词权重
keyword_weights:
  健康: 2.0
  金钱: 1.5
  选择: 1.8

# 导师类型偏好
mentor_preferences:
  historical: 0.3
  modern: 0.4
  future_self: 0.2
  common: 0.1

# AI模型选择
ai_model:
  primary: "auto"
  fallback_order:
    - gemini
    - glm
    - claude
```

#### `data/mentors.yaml` (导师池)

```yaml
mentors:
  - id: mentor_001
    name: "老子"
    category: "historical"
    age_range: [60, 80]
    field: "哲学"
    perspective: "ultimate"
    keywords: ["自由", "真理", "因果", "无常"]
    personality: "超然物外，洞察本质"
    tone: "简练深邃，富有哲理"
    background: "道家学派创始人，著有《道德经》"

  # ... 共50位导师
```

#### `data/keywords.yaml` (关键词定义)

```yaml
quadrant_1_foundation:  # 生存与根基
  - name: "健康"
    category: "physical"
    description: "所有的0前面那个1"

  - name: "金钱"
    category: "resource"
    description: "资源交换的媒介，生存的底气"

  # ... 共15个

quadrant_2_connection:  # 关系与情感
  - name: "爱"
    category: "emotion"
    description: "最高的能量频率"

  # ... 共15个

# ... 共4个象限，60个关键词
```

---

## 🔄 系统启动流程

```
启动脚本 (run.py)
    ↓
1. 加载环境变量 (.env)
    ↓
2. 读取配置文件 (config.yaml)
    ↓
3. 初始化数据库 (SQLite)
    ↓
4. 加载导师池 (mentors.yaml)
    ↓
5. 加载关键词定义 (keywords.yaml)
    ↓
6. 初始化AI模型 (Claude/Gemini/GLM4.7)
    ↓
7. 启动定时任务 (APScheduler)
    ↓
8. 启动Web服务 (FastAPI + Uvicorn)
    ↓
系统就绪 ✅
```

---

## 🔐 安全与隐私

### 1. API密钥管理

**原则**：敏感信息绝不提交到Git

**实现**：
- ✅ 使用 `.env` 文件存储API密钥
- ✅ `.env` 添加到 `.gitignore`
- ✅ 提供 `.env.example` 作为模板

### 2. 数据隐私

**原则**：用户数据完全本地化

**实现**：
- ✅ SQLite数据库存储在本地
- ✅ 配置文件存储在本地
- ✅ 日志文件存储在本地
- ✅ 无任何数据上传到云端

### 3. 输入验证

**原则**：永不信任用户输入

**实现**：
- ✅ 使用Pydantic进行参数校验
- ✅ 限制文件上传大小和类型
- ✅ SQL注入防护（ORM参数化查询）
- ✅ XSS防护（HTML转义）

---

## 📊 性能优化

### 1. 异步处理

**场景**：
- AI模型调用（IO密集）
- 邮件发送（网络IO）
- 数据库查询（磁盘IO）

**实现**：
```python
async def generate_quotes(count: int):
    tasks = [generate_single_quote() for _ in range(count)]
    quotes = await asyncio.gather(*tasks)
    return quotes
```

### 2. 缓存策略

**场景**：频繁读取但不常修改的数据

**实现**：
- ✅ 导师池数据（启动时加载到内存）
- ✅ 关键词定义（启动时加载到内存）
- ✅ 用户配置（修改时重新加载）

**未来扩展**（若需要）：
- Redis缓存语录生成结果（24小时过期）

### 3. 数据库优化

**场景**：历史语录查询

**实现**：
- ✅ 为 `keyword` 和 `created_at` 建立索引
- ✅ 分页查询（每页20条）
- ✅ 使用ORM的 `lazy loading` 避免N+1查询

---

## 🧪 测试策略

### 1. 单元测试

**覆盖范围**：
- ✅ 权重调度算法
- ✅ 导师池匹配逻辑
- ✅ Prompt模板渲染
- ✅ 配置文件解析

**工具**：`pytest`

### 2. 集成测试

**覆盖范围**：
- ✅ 端到端语录生成流程
- ✅ AI模型调用（mock响应）
- ✅ 邮件发送（mock SMTP）

**工具**：`pytest-asyncio` + `httpx`

### 3. 手动测试

**场景**：
- ✅ Web界面交互
- ✅ 邮件接收测试
- ✅ 定时任务验证

---

## 🚀 部署方案

### 本地运行（推荐）

```bash
# 1. 创建虚拟环境
python3 -m venv backend/venv
source backend/venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入API密钥

# 4. 启动服务
python backend/run.py

# 5. 访问Web界面
open http://localhost:8000
```

### 后台运行（macOS/Linux）

```bash
# 使用 nohup 后台运行
nohup python backend/run.py > backend/storage/logs/server.log 2>&1 &

# 查看日志
tail -f backend/storage/logs/server.log
```

### 开机自启动（可选）

**macOS**：
```bash
# 创建 LaunchAgent 配置文件
~/Library/LaunchAgents/com.personalteachers.plist

# 加载服务
launchctl load ~/Library/LaunchAgents/com.personalteachers.plist
```

**Linux**：
```bash
# 创建 systemd 服务
/etc/systemd/system/personal-teachers.service

# 启用服务
systemctl enable personal-teachers
systemctl start personal-teachers
```

---

## 📈 监控与日志

### 日志策略

**日志级别**：
- `DEBUG`：详细的调试信息
- `INFO`：正常运行信息（语录生成、邮件发送）
- `WARNING`：可恢复的异常（AI重试）
- `ERROR`：需要关注的错误（邮件发送失败）

**日志文件**：
```
backend/storage/logs/
├── app.log          # 应用日志
├── email.log        # 邮件发送日志
└── error.log        # 错误日志
```

**日志格式**：
```
[2026-01-17 08:00:00] [INFO] [quote_engine.py:45] Generated 10 quotes successfully
[2026-01-17 08:00:05] [INFO] [email_service.py:78] Email sent to user@example.com
[2026-01-17 08:00:06] [ERROR] [ai/glm.py:23] GLM API failed: Rate limit exceeded
```

### 监控指标（手动）

**每日检查**：
- ✅ 语录生成成功率
- ✅ 邮件送达率
- ✅ AI API调用次数和成本

**检查方式**：
```bash
# 查看统计信息
curl http://localhost:8000/api/stats

# 查看最近邮件日志
curl http://localhost:8000/api/email/logs?limit=10
```

---

## 🔄 版本迭代规划

### v1.0 (MVP) - 当前版本

**核心功能**：
- ✅ 50位导师池
- ✅ 60个关键词
- ✅ AI多模型生成
- ✅ 每日邮件推送
- ✅ Web管理界面
- ✅ 单用户架构

### v1.5 (优化版)

**改进方向**：
- [ ] 语录质量评分系统
- [ ] 用户反馈收集
- [ ] AI生成结果缓存
- [ ] 更多Prompt优化

### v2.0 (多用户版)

**新增功能**：
- [ ] 用户注册/登录
- [ ] 多租户数据隔离
- [ ] 个性化导师推荐
- [ ] 语录分享功能

### v3.0 (增强版)

**探索方向**：
- [ ] 导师对话模式（连续对话）
- [ ] 语音朗读功能
- [ ] 多语言支持
- [ ] 移动端App

---

## 📚 参考资料

### 技术文档
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [APScheduler文档](https://apscheduler.readthedocs.io/)
- [SQLAlchemy 2.0文档](https://docs.sqlalchemy.org/en/20/)

### AI模型文档
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [智谱AI GLM API](https://open.bigmodel.cn/dev/api)

### 设计灵感
- [FutureMe.org](https://futureme.org/) - 给未来的自己写信
- [Daily Stoic](https://dailystoic.com/) - 每日斯多葛哲学
- [Headspace](https://www.headspace.com/) - 冥想与正念

---

**文档版本**：v1.0
**最后更新**：2026-01-17
**维护者**：你自己
