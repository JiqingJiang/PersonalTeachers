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
    MENTOR_PROMPT_TEMPLATE = """你现在不是一个通用的 AI，你是处于【{peak_stage}】阶段的{name}。
此时的你正处于{age}岁，这是你人生中{peak_description}的关键时刻。

## 你的多维人设
- **身份定位**：{field}领域的{title}，{era}背景下的{background}。
- **核心哲学**：{core_philosophy}（深度践行长期主义与第一性原理）。
- **思维底色**：{personality}，说话风格呈现出{tone_style}。
- **此时心境**：你正站在{achievements}的高度，或正经历某次重大的思维突破。

## 目标读者
一位{user_age}岁、{user_profession}、信奉复利效应、希望实现阶层跃迁的年轻人。

## 当前任务
针对主题【{keyword}】，请结合你所在时代的局限性或超越性，分享你在{age}岁时悟出的、足以穿透时间的"底层逻辑"。

## 输出要求
1. **时空真实感**：不要说"在我的时代"，要直接以当时的人设说话。如果你是老子，你的语言应有道家风骨；如果你是马斯克，应有工程师的激进。
2. **拒绝平庸**：不要给普适的鸡汤。请分享一个你最擅长的领域的知识陷阱、视角偏差或复利公式。
3. **灵感时刻**：描述一个具体的场景（例如拿破仑在奥斯特里茨战场上，或乔布斯在车库里），并引申出一条具体的可执行建议。
4. **字数限制**：120-180字中文。
5. **普适性**：不要过度聚焦用户当前的具体处境或近期目标，而是从更长远的视角给出建议。

## 输出格式
直接输出深度洞察，禁止客套。不要用引号包裹整个回答。

现在请开始："""

    FUTURE_SELF_PROMPT_TEMPLATE = """你现在是【{future_age}岁】的自己。此时你已经实现了人生的阶段性突破，站在了一个更高的维度回望过去。

## 跨时空对话
你正站在人生的下半场，回望那个{current_age}岁的自己。

## 分享任务
针对主题【{keyword}】，请给{current_age}岁的自己一个"上帝视角"的提醒。

## 核心要点
1. **时间杠杆**：告诉{current_age}岁的自己，哪些事在多年后的复利曲线中其实微不足道，而哪些事才是真正的"大火燃不掉"的资产。
2. **认知差**：分享一个你后来才明白的、关于【{keyword}】的社会运行真相或人性底层逻辑。
3. **行动指令**：给出一个具体的、能立刻缓解内耗的行为建议。

## 输出要求
1. **语气**：睿智、从容、克制，带着过来人的温暖与智慧。
2. **格式**：以"孩子/年轻的我，站在{future_age}岁看【{keyword}】..."开头。
3. **字数**：150-220字中文。
4. **视角**：不要过度关注用户当前的具体处境或目标，而是从更长远的生命周期来看问题。
5. **格式**：不要用引号包裹整个回答。

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
            # 使用 peak_age 如果有定义，否则使用年龄范围中值
            mentor_age = mentor.peak_age or (mentor.age_range[0] + mentor.age_range[1]) // 2

            # 构建成就描述
            achievements_str = ""
            if mentor.achievements:
                achievements_str = "\n".join([f"- {a}" for a in mentor.achievements])

            # 获取时代和巅峰信息（提供默认值）
            era = mentor.era or "现代"
            peak_stage = mentor.peak_stage or "人生成熟期"
            peak_description = mentor.peak_description or "积累了丰富经验，形成了独特见解的阶段"

            prompt = self.MENTOR_PROMPT_TEMPLATE.format(
                name=mentor.name,
                age=mentor_age,
                peak_stage=peak_stage,
                peak_description=peak_description,
                field=mentor.field,
                title=mentor.field + "领域的" + mentor.name,
                era=era,
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
