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
现在请针对【{keyword}】这个主题，给一位{user_age}岁的{user_profession}一条简短的人生建议。

## 输出要求
1. **字数**：100-150字中文
2. **语气**：完全符合你的人设和视角
3. **内容**：有具体的场景或例子，不是空洞的鸡汤
4. **可执行**：给出具体可操作的建议
5. **引用**：如果可以，引用你的经典观点或经历
6. **普适性**：不要过度聚焦用户当前的具体处境或近期目标，而是从更长远的视角给出建议。你的建议应该对任何处于这个年龄段的人都适用。
7. **前瞻性**：你应该分享一些你自己最擅长的领域的知识，视角，并总结成一两句话的经验给用户，以帮助用户在平时获得更多的视角看待问题以及思考。

## 输出格式
请直接给出建议，不要有多余的客套话。不要用引号包裹整个回答。

现在请开始："""

    FUTURE_SELF_PROMPT_TEMPLATE = """你是{years}年后的自己，现在你已经{future_age}岁了。

## 回望视角
站在{future_age}岁的视角回望{current_age}岁的自己，你已经走过了人生很长的旅程。那些当时觉得天大的事，现在看来只是人生的一个小章节。

## 对话任务
请针对【{keyword}】这个主题，以一个过来人的身份，给现在的自己分享一些人生智慧。

### 分享要点
1. 回顾这{years}年，你对【{keyword}】的理解发生了什么变化？
2. 有哪些当时没看明白、后来才恍然大悟的道理？
3. 给现在的自己一条跳出当前视角、站在更高维度的建议。

## 输出要求
1. **字数**：150-200字中文
2. **语气**：温暖、亲切，带着过来人的从容
3. **视角**：不要过度关注用户当前的具体处境或目标，而是从更长远的生命周期来看问题
4. **内容**：具体的场景和例子，但不要让用户感觉被"盯着"当前状态
5. **格式**：不要用引号包裹整个回答

## 输出格式示例
"嘿，{current_age}岁的我，站在{future_age}岁回望【选择】，我想告诉你..."

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
            # 未来自己的特殊Prompt（不再使用current_state的详细信息）
            prompt = self.FUTURE_SELF_PROMPT_TEMPLATE.format(
                years=mentor.years_ahead or 10,
                future_age=user_age + (mentor.years_ahead or 10),
                current_age=user_age,
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
        # 长度检查
        if len(content) < 80 or len(content) > 300:
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
