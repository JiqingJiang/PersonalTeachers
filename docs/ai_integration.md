# PersonalTeachers AI集成文档

## 📖 文档概述

**为什么需要这个文档？**
- 明确AI模型的使用策略和集成方式
- 提供Prompt设计最佳实践
- 指导多模型容错和成本优化

**适合谁阅读？**
- 开发时集成AI模型
- 优化Prompt以提高生成质量
- 调整模型策略以降低成本

---

## 🎯 设计哲学

### 核心理念

> **AI是工具，不是目的。质量第一，成本第二，体验第三。**

### 多模型策略

#### 为什么要支持多模型？

1. **成本优化**：Gemini免费额度优先使用
2. **质量保障**：Claude作为高质量备选
3. **容错能力**：主模型失败时自动切换
4. **风格多样**：不同模型有不同的生成风格

#### 模型优先级

```
1. Gemini (免费) → 2. GLM4.7 (便宜) → 3. Claude (高质量)
```

**选择逻辑**：
```python
async def generate_with_fallback(prompt: str) -> str:
    """带降级策略的生成"""
    models = config['ai_model']['fallback_order']

    for model_name in models:
        try:
            provider = get_llm_provider(model_name)
            result = await provider.generate(prompt)
            if validate_quality(result):
                return result
        except Exception as e:
            logger.warning(f"{model_name} failed: {e}")
            continue

    # 所有模型都失败
    raise GenerationError("All AI models failed")
```

---

## 🤖 支持的AI模型

### 1. Claude (Anthropic)

**模型版本**：Claude 3.5 Sonnet

**优势**：
- ✅ 生成质量最高
- ✅ 中文理解能力强
- ✅ 逻辑推理能力出色
- ✅ 支持长上下文（200K tokens）

**劣势**：
- ❌ 成本较高（$3/1M input, $15/1M output）
- ❌ 免费额度有限

**适用场景**：
- 生成重要关键词的语录（如：选择、自由、意义）
- 未来自己的生成（需要更温暖的语气）
- 其他模型失败时的备选

**API配置**：
```python
# .env
ANTHROPIC_API_KEY=sk-ant-xxx

# config.yaml
ai_model:
  models:
    claude:
      model_name: "claude-3-5-sonnet-20241022"
      max_tokens: 500
      temperature: 0.7
      timeout: 30
```

**集成代码**：
```python
import anthropic

class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.messages.create,
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

---

### 2. Gemini (Google)

**模型版本**：Gemini 1.5 Pro

**优势**：
- ✅ **免费额度充足**（15次/分钟）
- ✅ 支持长上下文（1M tokens）
- ✅ 多模态能力（虽然我们只用文本）
- ✅ 响应速度快

**劣势**：
- ⚠️ 中文能力略逊于Claude
- ⚠️ 偶尔会有内容审查拒答

**适用场景**：
- **首选模型**（优先使用）
- 常规关键词的语录生成
- 成本敏感的批量生成

**API配置**：
```python
# .env
GOOGLE_API_KEY=AIzaSyxxx

# config.yaml
ai_model:
  models:
    gemini:
      model_name: "gemini-1.5-pro"
      max_tokens: 500
      temperature: 0.7
      timeout: 30
```

**集成代码**：
```python
import google.generativeai as genai

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    async def generate(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.7,
            )
        )
        return response.text
```

---

### 3. GLM4.7 (智谱AI)

**模型版本**：GLM-4-7B

**优势**：
- ✅ **成本极低**（¥1/1M input, ¥2/1M output）
- ✅ 中文能力强（国产模型）
- ✅ 响应速度快

**劣势**：
- ⚠️ 生成质量略逊于Claude
- ⚠️ 复杂逻辑推理能力一般

**适用场景**：
- Gemini失败时的备选
- 成本敏感的生成任务
- 中文语境的理解

**API配置**：
```python
# .env
ZHIPUAI_API_KEY=xxx.xxx

# config.yaml
ai_model:
  models:
    glm:
      model_name: "glm-4-flash"
      max_tokens: 500
      temperature: 0.7
      timeout: 30
```

**集成代码**：
```python
from zhipuai import ZhipuAI

class GLMProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = ZhipuAI(api_key=api_key)

    async def generate(self, prompt: str) -> str:
        response = await asyncio.to_thread(
            self.client.chat.completions.create,
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
```

---

## 🎨 Prompt设计最佳实践

### 核心原则

1. **明确角色**：让AI知道它是谁
2. **明确任务**：告诉AI要做什么
3. **明确约束**：规定输出的格式和长度
4. **提供上下文**：给AI足够的背景信息
5. **示例驱动**：如果可能，提供示例

### Prompt模板设计

#### 普通导师Prompt

```python
MENTOR_PROMPT_TEMPLATE = """
你是{name}，{age}岁的{field}领域的{title}。

## 你的核心观点
{core_philosophy}

## 你的性格特点
{personality}

## 你的说话风格
{tone_style}

## 你的背景经历
{background}

## 你的代表成就
{achievements}

## 当前任务
现在请针对【{keyword}】这个主题，给一位{user_age}岁的{user_profession}一条简短的人生建议。

## 用户当前状态
- 年龄：{user_age}岁
- 职业：{user_profession}
- 当前困惑：{current_confusion}
- 期望方向：{expectation}

## 输出要求
1. **字数**：100-150字中文
2. **语气**：完全符合你的人设和视角
3. **内容**：有具体的场景或例子，不是空洞的鸡汤
4. **可执行**：给出具体可操作的建议
5. **引用**：如果可以，引用你的经典观点或经历

## 输出格式
请直接给出建议，不要有多余的客套话。不要用引号包裹整个回答。

现在请开始：
"""
```

#### 未来自己Prompt

```python
FUTURE_SELF_PROMPT_TEMPLATE = """
你是{years}年后的自己，现在你已经{future_age}岁了。

## 现在的你（{current_age}岁）
- 年龄：{current_age}岁
- 职业：{user_profession}
- 当前状态：{current_status}
- 最大的困惑：{confusion}
- 期望的方向：{expectation}

## 未来的你（{future_age}岁）
想象一下，从{current_age}岁到{future_age}岁这{years}年：
- 你经历了什么？
- 你在【{keyword}】方面有什么心得？
- 你有哪些想告诉现在自己的话？

## 对话任务
请以温暖、理解、鼓励的语气，给现在的自己一些建议：

### 回顾
1. 回顾这{years}年，你在【{keyword}】方面最大的成长是什么？
2. 有哪些坑是现在的你可能遇到的，提前提醒一下？
3. 给现在的自己一条具体的、可执行的建议。

## 输出要求
1. **字数**：150-200字中文
2. **语气**：像未来的自己在对话，温暖、亲切、理解
3. **内容**：具体的场景和例子，不要空洞
4. **情感**：可以适当表达"我经历过，我理解"的情感共鸣
5. **格式**：不要用引号包裹整个回答

## 输出格式示例
"嘿，现在的我，还记得你在26岁时对【选择】的困惑吗？让我告诉你，38岁的我现在回过头看..."

现在请开始你的分享：
"""
```

### Prompt优化技巧

#### 1. 人设强化

**问题**：AI生成的内容不够符合人设

**解决**：增加人设描述的细节

```python
# 改进前
personality: "哲学家"

# 改进后
personality: """
你是一位道家哲学家，超然物外，洞察本质。
你说话简练深邃，常用比喻和反问。
你强调"道法自然"、"无为而治"。
你不推崇人为的努力，而强调顺应天道。
你的代表观点是："上善若水，水善利万物而不争。"
"""
```

#### 2. 风格约束

**问题**：AI生成的语气不符合预期

**解决**：明确指定语气和禁止事项

```python
# 改进前
tone: "温和的"

# 改进后
tone: """
你的语气应该：
- 温和、亲切、像老朋友聊天
- 不说教、不居高临下
- 多用"我"、"我们"而不是"你"
- 可以适当使用口语和比喻
- 禁止使用："你应该"、"你必须"、"一定要"
"""
```

#### 3. 质量约束

**问题**：AI生成的内容空洞或太短

**解决**：明确质量标准和检查清单

```python
quality_requirements = """
## 质量检查清单
在生成回答前，请自查：
1. ✅ 是否有具体的场景或例子？
2. ✅ 是否给出了可执行的建议？
3. ✅ 字数是否在100-150字之间？
4. ✅ 是否符合你的人设和视角？
5. ✅ 是否避免了空洞的鸡汤话？

如果以上任何一项不满足，请重新生成。
"""
```

---

## 🔄 容错与重试机制

### 三级容错策略

```python
class QuoteGenerator:
    async def generate_with_retry(
        self,
        keyword: str,
        mentor: Mentor,
        max_retries: int = 3
    ) -> Quote:
        """
        带重试机制的语录生成

        策略：
        1. 同一模型重试1次（可能是网络问题）
        2. 切换到下一个模型重试
        3. 如果所有模型都失败，抛出异常
        """
        models = config['ai_model']['fallback_order']

        for model_name in models:
            for attempt in range(max_retries):
                try:
                    provider = get_llm_provider(model_name)
                    prompt = self.build_prompt(keyword, mentor)
                    result = await provider.generate(prompt)

                    # 质量验证
                    if self.validate_quality(result):
                        return Quote(
                            mentor_name=mentor.name,
                            keyword=keyword,
                            content=result,
                            ai_model=model_name
                        )
                    else:
                        logger.warning(f"Quality check failed for {model_name}")
                        continue  # 重试

                except RateLimitError:
                    logger.warning(f"Rate limit: {model_name}, switching...")
                    break  # 切换模型
                except Exception as e:
                    logger.error(f"Error with {model_name}: {e}")
                    continue  # 重试

        raise GenerationError("All models failed after retries")
```

### 质量验证函数

```python
def validate_quality(content: str) -> bool:
    """
    验证生成内容的质量

    检查项：
    1. 长度是否在合理范围（80-200字）
    2. 是否包含敏感词
    3. 是否为空或过短
    4. 是否包含拒绝回复的话术
    """
    # 长度检查
    if len(content) < 80 or len(content) > 200:
        return False

    # 拒绝回复检查
    reject_phrases = [
        "我无法提供",
        "我不建议",
        "这个问题不适合",
        "作为AI",
    ]
    if any(phrase in content for phrase in reject_phrases):
        return False

    # 敏感词检查
    sensitive_words = ["暴力", "自杀", "违法"]
    if any(word in content for word in sensitive_words):
        return False

    return True
```

---

## 💰 成本优化策略

### 成本对比

| 模型 | 输入成本 | 输出成本 | 单条估算（500tokens） |
|------|----------|----------|---------------------|
| Claude 3.5 Sonnet | $3/1M | $15/1M | ~$0.009 |
| Gemini 1.5 Pro | 免费 | 免费 | $0 |
| GLM-4-Flash | ¥0.1/1M | ¥0.1/1M | ~¥0.0001 |

**月度成本估算**（每天10条）：
- Claude：~$2.7/月
- Gemini：$0（免费额度内）
- GLM4.7：~¥0.03/月

### 优化策略

#### 1. 优先使用免费模型

```python
# config.yaml
ai_model:
  primary: "auto"  # 自动选择
  fallback_order:
    - gemini  # 优先（免费）
    - glm     # 备选（便宜）
    - claude  # 最后（高质量）
```

#### 2. 重要内容用高质量模型

```python
# 根据关键词重要性选择模型
IMPORTANT_KEYWORDS = ["选择", "自由", "意义", "自我", "健康"]

def select_model_for_keyword(keyword: str) -> str:
    """根据关键词选择模型"""
    if keyword in IMPORTANT_KEYWORDS:
        return "claude"  # 重要关键词用Claude
    else:
        return "auto"    # 其他用自动选择
```

#### 3. 缓存机制（未来扩展）

```python
# 未来可以考虑缓存常见关键词的生成结果
# 24小时内相同关键词+导师组合，直接返回缓存
cache = TTLCache(maxsize=1000, ttl=86400)

async def generate_with_cache(keyword: str, mentor: Mentor):
    cache_key = f"{keyword}:{mentor.id}"

    if cached := cache.get(cache_key):
        return cached

    result = await generate_quote(keyword, mentor)
    cache[cache_key] = result
    return result
```

#### 4. 批量生成优化

```python
# 如果一次生成多条，可以并行调用
async def generate_batch(keywords: list[str]) -> list[Quote]:
    tasks = [generate_single_quote(kw) for kw in keywords]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 过滤失败的
    return [r for r in results if isinstance(r, Quote)]
```

---

## 🧪 测试与调优

### 单元测试

```python
# tests/test_ai_models.py
import pytest

@pytest.mark.asyncio
async def test_claude_provider():
    provider = ClaudeProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    result = await provider.generate("测试Prompt")
    assert len(result) > 0
    assert "测试" not in result  # 不应该包含Prompt本身

@pytest.mark.asyncio
async def test_gemini_provider():
    provider = GeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"))
    result = await provider.generate("测试Prompt")
    assert len(result) > 0

@pytest.mark.asyncio
async def test_glm_provider():
    provider = GLMProvider(api_key=os.getenv("ZHIPUAI_API_KEY"))
    result = await provider.generate("测试Prompt")
    assert len(result) > 0
```

### Prompt A/B测试

```python
# 测试不同Prompt的效果
async def test_prompt_variants():
    variants = [
        "variant_a": prompt_v1,
        "variant_b": prompt_v2,
        "variant_c": prompt_v3,
    ]

    results = {}
    for name, prompt in variants.items():
        quality_scores = []
        for _ in range(10):
            result = await generate_with_prompt(prompt)
            score = rate_quality(result)  # 人工或自动评分
            quality_scores.append(score)

        results[name] = {
            "avg_score": np.mean(quality_scores),
            "std_score": np.std(quality_scores)
        }

    # 选择平均分最高的Prompt
    best = max(results.items(), key=lambda x: x[1]["avg_score"])
    return best
```

### 质量监控

```python
# 记录每次生成的元数据
class QuoteMetadata:
    keyword: str
    mentor_id: str
    ai_model: str
    prompt_template: str
    generated_at: datetime
    quality_score: float  # 用户评分
    token_count: int
    generation_time: float

# 定期分析
async def analyze_quality():
    """分析各模型的生成质量"""
    stats = await db.get_quality_stats()

    for model in ["claude", "gemini", "glm"]:
        model_stats = [s for s in stats if s.ai_model == model]
        avg_quality = np.mean([s.quality_score for s in model_stats])
        avg_time = np.mean([s.generation_time for s in model_stats])

        print(f"{model}:")
        print(f"  Avg Quality: {avg_quality:.2f}")
        print(f"  Avg Time: {avg_time:.2f}s")
```

---

## 🚨 错误处理

### 常见错误类型

```python
class AIError(Exception):
    """AI相关错误的基类"""
    pass

class RateLimitError(AIError):
    """API速率限制"""
    pass

class QuotaExceededError(AIError):
    """配额用尽"""
    pass

class ContentFilterError(AIError):
    """内容审核拒绝"""
    pass

class NetworkError(AIError):
    """网络错误"""
    pass

class TimeoutError(AIError):
    """超时"""
    pass
```

### 错误处理策略

```python
async def handle_ai_error(error: Exception, model: str) -> str:
    """处理AI错误"""
    if isinstance(error, RateLimitError):
        logger.warning(f"Rate limit hit for {model}, switching model...")
        return "switch_model"

    elif isinstance(error, QuotaExceededError):
        logger.error(f"Quota exceeded for {model}")
        return "switch_model"

    elif isinstance(error, ContentFilterError):
        logger.warning(f"Content filtered by {model}")
        return "retry_with_relaxed_prompt"

    elif isinstance(error, NetworkError):
        logger.warning(f"Network error with {model}")
        return "retry"

    elif isinstance(error, TimeoutError):
        logger.warning(f"Timeout with {model}")
        return "retry"

    else:
        logger.error(f"Unknown error with {model}: {error}")
        return "switch_model"
```

---

## 📊 性能监控

### 关键指标

```python
class AIMetrics:
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    total_tokens_used: int
    total_cost: float
    by_model: dict[str, ModelMetrics]
```

### 监控仪表板

```python
# 可选：实现简单的监控接口
@app.get("/api/ai/metrics")
async def get_ai_metrics():
    """获取AI使用统计"""
    metrics = await load_ai_metrics()
    return {
        "today": {
            "requests": metrics.total_requests_today,
            "success_rate": metrics.success_rate,
            "avg_time": metrics.avg_response_time,
            "cost": metrics.total_cost_today,
        },
        "by_model": {
            "claude": {
                "usage": metrics.claude_usage,
                "cost": metrics.claude_cost,
            },
            # ...
        }
    }
```

---

## 📚 参考资源

### API文档
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/docs)
- [智谱AI GLM API](https://open.bigmodel.cn/dev/api)

### Prompt工程
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Prompt Library](https://docs.anthropic.com/claude/prompt-library)

### 成本优化
- [Token计算器](https://tokenmeter.net/)
- [AI成本对比](https://artificialanalysis.ai/)

---

**文档版本**：v1.0
**最后更新**：2026-01-17
