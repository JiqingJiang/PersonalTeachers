"""语录生成引擎

复用 v1 的双 Prompt 模板（常规导师 vs 未来自己），改用 asyncio.gather 并行生成。
"""

import asyncio
from datetime import datetime
from loguru import logger

from app.ai.fallback_chain import FallbackChain
from app.core.keyword_scheduler import KeywordScheduler
from app.core.mentor_pool import MentorPool
from app.core.quality import validate_quality

# ===== Prompt 模板（复用 v1）=====

MENTOR_PROMPT_TEMPLATE = """你现在是{name}，{era_desc}{field_desc}。

你的性格特质：{personality}
你的说话风格：{tone}
{peak_context}
用户正在寻求关于「{keyword}」的人生智慧。

请以{name}的口吻和视角，给出一段关于「{keyword}」的人生感悟或建议。

要求：
1. 以第一人称说话，仿佛你就是{name}本人
2. 结合你的人生经历和{field_desc2}来谈论{keyword}
3. 语气要{tone}
4. 内容要有深度、有洞察力，能给人启发
5. 长度在50-100字之间
6. 不要出现"作为AI"等机器人的话

请直接输出你的感悟，不需要标题或格式："""

FUTURE_SELF_PROMPT_TEMPLATE = """你是{years_ahead}年后的{user_name}，一个经历过人生风雨、获得深刻智慧的{future_age}岁的人。

你现在的状态：{current_stage}
你的核心智慧来源：你曾经经历过{user_age}岁时{user_name}正在经历的一切

用户（也就是{years_ahead}年前的你）正在寻求关于「{keyword}」的人生智慧。

请以未来自己的口吻，给现在的自己一段关于「{keyword}」的感悟。

要求：
1. 以"你"来称呼过去的自己
2. 带着过来人的从容和温暖
3. 既要有深刻的人生洞察，又要有实际的可操作性
4. 长度在50-100字之间
5. 不要出现"作为AI"等机器人的话

请直接输出你的感悟："""


class QuoteEngine:
    """语录生成引擎"""

    def __init__(self):
        self.keyword_scheduler = KeywordScheduler()
        self.fallback_chain = FallbackChain(max_retries=2)

    async def generate_quotes_for_user(
        self,
        user: dict,
        keywords: list[dict],
        mentors: list[dict],
        user_keyword_weights: dict[int, float] | None,
        user_mentor_ids: set[int] | None,
        model_configs: list[dict],
        count: int = 10,
    ) -> list[dict]:
        """
        为用户生成一批语录。

        Args:
            user: 用户信息（nickname, age, profession, mentor_category_prefs）
            keywords: 可用关键词列表
            mentors: 可用导师列表
            user_keyword_weights: 用户自定义关键词权重
            user_mentor_ids: 用户启用的导师 ID 集合
            model_configs: AI 模型配置（按优先级排序）
            count: 生成数量

        Returns:
            语录列表 [{"mentor_name", "mentor_category", "keyword", "content", "ai_model"}]
        """
        # 1. 选择关键词
        selected_keywords = self.keyword_scheduler.select_keywords(
            keywords=keywords,
            user_weights=user_keyword_weights,
            count=count,
        )

        if not selected_keywords:
            logger.warning("没有可选的关键词")
            return []

        # 2. 构建导师池
        mentor_pool = MentorPool(mentors)
        category_prefs = user.get("mentor_category_prefs")

        # 3. 为每个关键词选择导师
        keyword_mentor_pairs = []
        used_mentor_ids: set[int] = set()

        for kw in selected_keywords:
            mentor = mentor_pool.select_mentor_for_keyword(
                keyword_name=kw["name"],
                category_prefs=category_prefs,
                enabled_mentor_ids=user_mentor_ids,
                exclude_ids=used_mentor_ids,
            )
            if mentor is None:
                # 没有匹配的导师，放宽条件重试
                mentor = mentor_pool.select_mentor_for_keyword(
                    keyword_name=kw["name"],
                    category_prefs=category_prefs,
                    enabled_mentor_ids=user_mentor_ids,
                    exclude_ids=None,
                )
            if mentor:
                keyword_mentor_pairs.append((kw, mentor))
                used_mentor_ids.add(mentor["id"])

        if not keyword_mentor_pairs:
            logger.warning("没有匹配的导师-关键词对")
            return []

        # 4. 并行生成语录（含补生成）
        quotes = await self._generate_batch(keyword_mentor_pairs, user, model_configs)

        # 如果数量不足，用未使用的导师-关键词对补生成
        retry_round = 0
        while len(quotes) < count and retry_round < 2:
            retry_round += 1
            need = count - len(quotes)
            # 重新选择关键词和导师
            extra_keywords = self.keyword_scheduler.select_keywords(
                keywords=keywords,
                user_weights=user_keyword_weights,
                count=need,
            )
            used_mentor_names = {q["mentor_name"] for q in quotes}
            extra_pairs = []
            for kw in extra_keywords:
                mentor = mentor_pool.select_mentor_for_keyword(
                    keyword_name=kw["name"],
                    category_prefs=category_prefs,
                    enabled_mentor_ids=user_mentor_ids,
                    exclude_ids=None,
                )
                if mentor:
                    extra_pairs.append((kw, mentor))

            if not extra_pairs:
                break

            extra_quotes = await self._generate_batch(extra_pairs, user, model_configs)
            quotes.extend(extra_quotes)
            logger.info(f"补生成第 {retry_round} 轮: +{len(extra_quotes)} 条，当前 {len(quotes)}/{count}")

        logger.info(f"成功生成 {len(quotes)}/{count} 条语录")
        return quotes

    async def _generate_batch(
        self,
        pairs: list[tuple[dict, dict]],
        user: dict,
        model_configs: list[dict],
    ) -> list[dict]:
        """批量生成语录"""
        semaphore = asyncio.Semaphore(3)

        async def generate_one(kw: dict, mentor: dict) -> dict | None:
            async with semaphore:
                return await self._generate_single(kw, mentor, user, model_configs)

        tasks = [generate_one(kw, m) for kw, m in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        quotes = []
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"生成语录异常: {r}")
                continue
            if r is not None:
                quotes.append(r)
        return quotes

    async def _generate_single(
        self,
        keyword: dict,
        mentor: dict,
        user: dict,
        model_configs: list[dict],
    ) -> dict | None:
        """生成单条语录"""
        prompt = self._build_prompt(keyword, mentor, user)

        try:
            content, model_name = await self.fallback_chain.generate(
                prompt=prompt,
                model_configs=model_configs,
                max_tokens=300,
                temperature=0.7,
            )

            if not validate_quality(content):
                logger.warning(f"语录质量不达标: {content[:50]}...")
                return None

            return {
                "mentor_name": mentor["name"],
                "mentor_category": mentor.get("category", ""),
                "keyword": keyword["name"],
                "content": content,
                "ai_model": model_name,
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"生成语录失败 ({mentor['name']} + {keyword['name']}): {e}")
            return None

    def _build_prompt(self, keyword: dict, mentor: dict, user: dict) -> str:
        """构建 Prompt"""
        # 未来自己类别使用独立模板
        if mentor.get("category") == "future_self":
            return self._build_future_self_prompt(keyword, mentor, user)
        return self._build_mentor_prompt(keyword, mentor, user)

    def _build_mentor_prompt(self, keyword: dict, mentor: dict, user: dict) -> str:
        """常规导师 Prompt"""
        era_desc = f"生活在{mentor.get('era', '')}，" if mentor.get("era") else ""
        field_desc = f"在{mentor.get('field', '')}领域有深厚造诣。" if mentor.get("field") else "一位智者。"
        field_desc2 = mentor.get("field", "人生") or "人生"

        # 灵感巅峰时刻
        peak_context = ""
        if mentor.get("peak_stage"):
            peak_context = f"你的人生灵感巅峰时刻：{mentor.get('peak_age', '')}岁时，{mentor.get('peak_stage', '')}。{mentor.get('peak_description', '')}"

        return MENTOR_PROMPT_TEMPLATE.format(
            name=mentor["name"],
            era_desc=era_desc,
            field_desc=field_desc,
            personality=mentor.get("personality", "沉稳睿智"),
            tone=mentor.get("tone", "平和而坚定"),
            peak_context=peak_context,
            keyword=keyword["name"],
            field_desc2=field_desc2,
        )

    def _build_future_self_prompt(self, keyword: dict, mentor: dict, user: dict) -> str:
        """未来自己 Prompt"""
        user_age = user.get("age") or 24
        user_name = user.get("nickname", "你")
        years_ahead = mentor.get("years_ahead", 5)
        future_age = user_age + years_ahead

        stage_map = {
            3: "刚刚走过这段迷茫期，已经看清了方向",
            5: "跨过了你正担心的那道坎，站得更稳了",
            10: "人生阅历丰富，对很多事情有了新的理解",
            20: "大半人生已过，拥有跨代的智慧",
            60: "在生命的尽头回望，看到了最本质的东西",
        }
        current_stage = stage_map.get(years_ahead, "拥有更广阔的人生视野")

        return FUTURE_SELF_PROMPT_TEMPLATE.format(
            years_ahead=years_ahead,
            user_name=user_name,
            future_age=future_age,
            current_stage=current_stage,
            user_age=user_age,
            keyword=keyword["name"],
        )
