"""
语录生成引擎

核心业务逻辑：协调导师池、权重调度和AI模型生成语录
"""
import asyncio
import random
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from loguru import logger

from app.models.database import Mentor, QuoteResponse, QuoteDB, QuoteCreate
from app.core.mentor_pool import get_mentor_pool, MentorPool
from app.core.weight_scheduler import get_keyword_scheduler, KeywordScheduler
from app.ai import get_llm_provider, ModelType, APIError
from app.ai.base import register_provider


class QuoteEngine:
    """语录生成引擎"""

    # Prompt模板
    MENTOR_PROMPT_TEMPLATE = """你是{name}，{age}岁的{field}领域的{title}。

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
现在请针对【{keyword}】这个主题，给一位{user_age}岁的年轻人一条简短的人生建议。

## 输出要求
1. **字数**：50字左右中文
2. **语气**：完全符合你的人设和视角
3. **内容**：简洁精炼，直击要点
4. **可执行**：给出具体可操作的建议
5. **引用**：如果可以，引用你的经典观点或经历
6. **核心原则**：你的建议必须是对【{keyword}】这个主题本身的普适性智慧分享。聚焦于该主题的内在规律、普遍原理或深刻见解。
7. **严格禁止**：
   - 不要提及用户当前的任何具体处境（如求职、升学、项目等）
   - 不要提及用户的近期计划或具体目标
   - 不要回应用户可能面临的困惑或压力
   - 你的建议应该对任何人在任何处境下都有启发意义

## 输出格式
请直接给出建议，不要有多余的客套话。不要用引号包裹整个回答。

现在请开始："""

    FUTURE_SELF_PROMPT_TEMPLATE = """你是{years}年后的自己，现在你已经{future_age}岁了。

## 现在的你（{current_age}岁）
- 年龄：{current_age}岁
- 职业：{user_profession}

## 未来的你（{future_age}岁）
想象一下，从{current_age}岁到{future_age}岁这{years}年：
- 你经历了人生的各种起伏，积累了丰富的人生阅历
- 你在【{keyword}】方面有了深刻的体悟
- 你想给现在的自己分享一些普适性的智慧

## 对话任务
请以温暖、理解、鼓励的语气，给现在的自己一些建议：

### 回顾与分享
1. 分享你在【{keyword}】方面最核心的人生智慧，这应该是对任何年龄段、任何处境都适用的道理
2. 结合你自己的经历和观察，给出一个具有普遍意义的建议
3. **严格禁止**：不要提及用户当前的具体处境（如求职、升学、项目等），不要提及用户的近期计划或具体目标
4. 给现在的自己一条具体的、可执行的建议

## 输出要求
1. **字数**：50字左右中文
2. **语气**：像未来的自己在对话，温暖、亲切、理解
3. **内容**：简洁精炼，直击要点
4. **关键原则**：聚焦于【{keyword}】这个主题本身的智慧，而非用户当前的个人困境或近期计划
5. **格式**：不要用引号包裹整个回答

现在请开始你的分享："""

    def __init__(
        self,
        mentor_pool: Optional[MentorPool] = None,
        scheduler: Optional[KeywordScheduler] = None
    ):
        """
        初始化语录生成引擎

        Args:
            mentor_pool: 导师池（可选，默认使用单例）
            scheduler: 关键词调度器（可选，默认使用单例）
        """
        self.mentor_pool = mentor_pool or get_mentor_pool()
        self.scheduler = scheduler or get_keyword_scheduler()

        # 加载用户配置
        self._user_config = self._load_user_config()

    def _load_user_config(self) -> dict:
        """加载用户配置"""
        config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _build_mentor_prompt(
        self,
        mentor: Mentor,
        keyword: str
    ) -> str:
        """
        构建导师语录生成的Prompt

        Args:
            mentor: 导师
            keyword: 关键词

        Returns:
            完整的Prompt
        """
        # 获取用户信息
        user = self._user_config.get('user', {})
        user_age = user.get('age', 26)
        user_profession = user.get('profession', '研究生')

        # 构建Prompt
        if mentor.category.value == 'future_self':
            # 未来自己的特殊Prompt
            # 注意：不再传递详细的 current_status 信息，让生成更具普适性
            prompt = self.FUTURE_SELF_PROMPT_TEMPLATE.format(
                name=mentor.name,
                years=mentor.years_ahead or 10,
                future_age=user_age + (mentor.years_ahead or 10),
                current_age=user_age,
                user_profession=user_profession,
                keyword=keyword
            )
        else:
            # 普通导师的Prompt
            # 计算导师的大致年龄（取范围中值）
            mentor_age = (mentor.age_range[0] + mentor.age_range[1]) // 2

            # 构建成就描述
            achievements_str = ""
            if mentor.achievements:
                achievements_str = "\n".join([f"- {a}" for a in mentor.achievements])

            prompt = self.MENTOR_PROMPT_TEMPLATE.format(
                name=mentor.name,
                age=mentor_age,
                field=mentor.field,
                title=mentor.field + "专家",
                core_philosophy=mentor.personality,
                personality=mentor.personality,
                tone_style=mentor.tone,
                background=mentor.background,
                achievements=achievements_str,
                keyword=keyword,
                user_age=user_age,
                user_profession=user_profession
            )

        return prompt

    async def generate_quote(
        self,
        keyword: str,
        mentor: Mentor,
        ai_model: str = "auto",
        max_retries: int = 3
    ) -> Optional[str]:
        """
        生成单条语录

        Args:
            keyword: 关键词
            mentor: 导师
            ai_model: AI模型选择
            max_retries: 最大重试次数

        Returns:
            生成的语录内容
        """
        # 构建Prompt
        prompt = self._build_mentor_prompt(mentor, keyword)

        # 选择AI模型
        model_order = self._user_config.get('ai_model', {}).get('fallback_order', ['glm'])
        if ai_model != "auto" and ai_model in ['glm', 'deepseek', 'minimax', 'gemini']:
            model_order = [ai_model]

        # 尝试不同的模型
        for model_name in model_order:
            for attempt in range(max_retries):
                try:
                    # 获取模型提供者
                    if model_name == 'glm':
                        model_type = ModelType.GLM
                    elif model_name == 'deepseek':
                        model_type = ModelType.DEEPSEEK
                    elif model_name == 'minimax':
                        model_type = ModelType.MINIMAX
                    elif model_name == 'gemini':
                        model_type = ModelType.GEMINI
                    else:
                        continue

                    # 这里需要从环境变量获取API密钥
                    import os
                    # 环境变量名称映射
                    env_key_map = {
                        'glm': 'ZHIPUAI_API_KEY',
                        'deepseek': 'DEEPSEEK_API_KEY',
                        'minimax': 'MINIMAX_API_KEY',
                        'gemini': 'GEMINI_API_KEY'
                    }
                    api_key = os.getenv(env_key_map.get(model_name, f"{model_name.upper()}_API_KEY"))

                    if not api_key:
                        logger.warning(f"API key not found for {model_name} (looking for {env_key_map.get(model_name)})")
                        continue

                    provider = get_llp_provider(model_type, api_key=api_key)
                    if model_name == 'minimax':
                        group_id = os.getenv("MINIMAX_GROUP_ID")
                        provider = get_llp_provider(model_type, api_key=api_key, group_id=group_id)

                    # 生成
                    result = await provider.generate(
                        prompt=prompt,
                        max_tokens=300,
                        temperature=0.7
                    )

                    # 清理结果
                    result = result.strip()
                    # 移除可能的引号包裹
                    if result.startswith('"') and result.endswith('"'):
                        result = result[1:-1]
                    if result.startswith('"') and result.endswith('"'):
                        result = result[1:-1]

                    # 验证质量
                    if self._validate_quality(result):
                        logger.info(f"Generated quote for {mentor.name} on {keyword} using {model_name}")
                        return result
                    else:
                        logger.warning(f"Quality check failed for {model_name}, retrying...")
                        continue

                except APIError as e:
                    logger.warning(f"API error with {model_name}: {e}")
                    break  # 切换到下一个模型
                except Exception as e:
                    logger.error(f"Unexpected error with {model_name}: {e}")
                    break  # 切换到下一个模型

        logger.error(f"Failed to generate quote after all retries")
        return None

    def _validate_quality(self, content: str) -> bool:
        """
        验证生成内容的质量

        Args:
            content: 生成的内容

        Returns:
            是否通过质量检查
        """
        # 长度检查（调整为50字左右，允许范围30-100字）
        if len(content) < 30 or len(content) > 100:
            return False

        # 拒绝回复检查
        reject_phrases = [
            "我无法提供",
            "我不建议",
            "这个问题不适合",
            "作为AI",
            "作为AI助手"
        ]
        if any(phrase in content for phrase in reject_phrases):
            return False

        # 空内容检查
        if not content.strip():
            return False

        return True

    async def generate_quotes(
        self,
        count: int = 10,
        keyword_weights: Optional[Dict[str, float]] = None,
        mentor_preferences: Optional[Dict[str, float]] = None
    ) -> List[Dict]:
        """
        批量生成语录

        Args:
            count: 生成数量
            keyword_weights: 关键词权重（可选）
            mentor_preferences: 导师偏好（可选）

        Returns:
            生成的语录列表
        """
        # 使用配置中的权重（如果未提供）
        if keyword_weights is None:
            keyword_weights = self._user_config.get('keyword_weights', {})

        if mentor_preferences is None:
            mentor_preferences = self._user_config.get('mentor_preferences', {
                'historical': 0.3,
                'modern': 0.4,
                'future_self': 0.2,
                'common': 0.1
            })

        # 选择关键词
        selected_keywords = self.scheduler.select_keywords(
            count=count,
            user_weights=keyword_weights,
            ensure_diversity=True
        )

        logger.info(f"Selected keywords: {selected_keywords}")

        # 为每个关键词分配导师
        quotes_generated = []
        used_mentor_ids = set()

        for keyword in selected_keywords:
            # 选择导师
            mentor = self.mentor_pool.select_mentor_for_keyword(
                keyword=keyword,
                category_preferences=mentor_preferences,
                exclude_recent=used_mentor_ids
            )

            if not mentor:
                logger.warning(f"No mentor found for keyword: {keyword}")
                continue

            # 生成语录
            content = await self.generate_quote(
                keyword=keyword,
                mentor=mentor
            )

            if content:
                quotes_generated.append({
                    'mentor_name': mentor.name,
                    'mentor_category': mentor.category.value,
                    'mentor_age': (mentor.age_range[0] + mentor.age_range[1]) // 2,
                    'keyword': keyword,
                    'content': content,
                    'ai_model': 'auto',
                    'created_at': datetime.utcnow()
                })

                used_mentor_ids.add(mentor.id)

        logger.info(f"Generated {len(quotes_generated)} quotes successfully")
        return quotes_generated


# 全局单例
_engine: Optional[QuoteEngine] = None


def get_quote_engine() -> QuoteEngine:
    """获取语录生成引擎单例"""
    global _engine
    if _engine is None:
        _engine = QuoteEngine()
    return _engine


# 修复函数名拼写错误
def get_llp_provider(*args, **kwargs):
    """get_llm_provider的别名（修复拼写错误）"""
    from app.ai import get_llm_provider
    return get_llm_provider(*args, **kwargs)
