"""语录生成引擎

复用 v1 的双 Prompt 模板（常规导师 vs 未来自己），改用 asyncio.gather 并行生成。
支持用户自定义字数、个性化背景和去重。
"""

import asyncio
from datetime import datetime
from loguru import logger

from app.ai.fallback_chain import FallbackChain
from app.config import get_settings
from app.core.keyword_scheduler import KeywordScheduler
from app.core.mentor_pool import MentorPool
from app.core.quality import validate_quality

# ===== Prompt 模板 =====

MENTOR_PROMPT_TEMPLATE = """你现在是{name}，{era_desc}{field_desc}

你的性格特质：{personality}
你的说话风格：{tone}
{peak_context}
{personal_context}用户正在寻求关于「{keyword}」的人生智慧。

请以{name}的口吻和视角，给出一段关于「{keyword}」的人生感悟或建议。

要求：
1. 以第一人称说话，仿佛你就是{name}本人
2. 结合你的人生经历和{field_desc2}来谈论{keyword}
3. 语气要{tone}
4. 内容要有深度、有洞察力，能给人启发
5. 长度在{min_words}-{max_words}字之间
6. 不要出现"作为AI"等机器人的话
{avoid_dup_context}
请直接输出你的感悟，不需要标题或格式："""

FUTURE_SELF_PROMPT_TEMPLATE = """你是{years_ahead}年后的{user_name}，一个经历过人生风雨、获得深刻智慧的{future_age}岁的人。

你现在的状态：{current_stage}
你的核心智慧来源：你曾经经历过{user_age}岁时{user_name}正在经历的一切
{personal_context}
用户（也就是{years_ahead}年前的你）正在寻求关于「{keyword}」的人生智慧。

请以未来自己的口吻，给现在的自己一段关于「{keyword}」的感悟。

要求：
1. 以"你"来称呼过去的自己
2. 带着过来人的从容和温暖
3. 既要有深刻的人生洞察，又要有实际的可操作性
4. 长度在{min_words}-{max_words}字之间
5. 不要出现"作为AI"等机器人的话
{avoid_dup_context}
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
        max_words: int = 100,
        recent_contents: list[str] | None = None,
    ) -> list[dict]:
        """
        为用户生成一批语录。保证返回数量等于 count，除非资源耗尽。
        """
        min_words = max(20, max_words // 4)

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

        # 3. 为每个关键词选择导师（尽量不重复）
        keyword_mentor_pairs = []
        used_mentor_ids: set[int] = set()

        for kw in selected_keywords:
            # 第一次尝试：排除已用的导师
            mentor = mentor_pool.select_mentor_for_keyword(
                keyword_name=kw["name"],
                category_prefs=category_prefs,
                enabled_mentor_ids=user_mentor_ids,
                exclude_ids=used_mentor_ids,
            )
            if mentor is None:
                # 第二次尝试：不排除已用导师，但从更大范围选
                mentor = mentor_pool.select_mentor_for_keyword(
                    keyword_name=kw["name"],
                    category_prefs=category_prefs,
                    enabled_mentor_ids=user_mentor_ids,
                    exclude_ids=None,
                )
            if mentor is not None:
                keyword_mentor_pairs.append((kw, mentor))
                used_mentor_ids.add(mentor["id"])

        if not keyword_mentor_pairs:
            logger.warning("没有匹配的导师-关键词对")
            return []

        # 4. 生成上下文
        gen_context = {
            "min_words": min_words,
            "max_words": max_words,
            "recent_contents": recent_contents or [],
        }

        # 5. 并行生成第一轮
        quotes = await self._generate_batch(keyword_mentor_pairs, user, model_configs, gen_context)

        # 6. 如果数量不足，补生成（最多5轮）
        max_retry_rounds = 5
        retry_round = 0
        while len(quotes) < count and retry_round < max_retry_rounds:
            retry_round += 1
            need = count - len(quotes)
            extra_keywords = self.keyword_scheduler.select_keywords(
                keywords=keywords,
                user_weights=user_keyword_weights,
                count=need,
            )
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

            extra_quotes = await self._generate_batch(extra_pairs, user, model_configs, gen_context)
            quotes.extend(extra_quotes)
            logger.info(f"补生成第 {retry_round} 轮: +{len(extra_quotes)} 条，当前 {len(quotes)}/{count}")

        # 7. 最终截断到 count 条，避免超出
        quotes = quotes[:count]

        logger.info(f"最终生成 {len(quotes)}/{count} 条语录")
        return quotes

    async def _generate_batch(
        self,
        pairs: list[tuple[dict, dict]],
        user: dict,
        model_configs: list[dict],
        gen_context: dict,
    ) -> list[dict]:
        """批量生成语录"""
        semaphore = asyncio.Semaphore(get_settings().LLM_CONCURRENCY)

        async def generate_one(kw: dict, mentor: dict) -> dict | None:
            async with semaphore:
                return await self._generate_single(kw, mentor, user, model_configs, gen_context)

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
        gen_context: dict,
    ) -> dict | None:
        """生成单条语录"""
        prompt = self._build_prompt(keyword, mentor, user, gen_context)

        max_words = gen_context.get("max_words", 100)
        # max_tokens 留足余量，避免 AI 被截断
        max_tokens = min(max(max_words * 3, 200), 600)

        try:
            content, model_name = await self.fallback_chain.generate(
                prompt=prompt,
                model_configs=model_configs,
                max_tokens=max_tokens,
                temperature=0.7,
            )

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

    def _is_too_similar(self, content: str, recent_contents: list[str], threshold: float = 0.75) -> bool:
        """
        检查内容是否与近期内容过于相似。
        使用字符级 Jaccard 相似度检测，阈值为 0.75（较高，只过滤高度重复的内容）。
        """
        content_chars = set(content)
        for recent in recent_contents:
            recent_chars = set(recent)
            if not content_chars or not recent_chars:
                continue
            # Jaccard 相似度：交集 / 并集
            intersection = len(content_chars & recent_chars)
            union = len(content_chars | recent_chars)
            if union == 0:
                continue
            similarity = intersection / union
            if similarity > threshold:
                return True
        return False

    def _build_prompt(self, keyword: dict, mentor: dict, user: dict, gen_context: dict) -> str:
        """构建 Prompt"""
        if mentor.get("category") == "future_self":
            return self._build_future_self_prompt(keyword, mentor, user, gen_context)
        return self._build_mentor_prompt(keyword, mentor, user, gen_context)

    def _build_personal_context(self, user: dict) -> str:
        """根据个性化权重构建用户背景上下文"""
        weight = user.get("personalization_weight", 0.5)
        bio = user.get("personal_bio", "")
        profession = user.get("profession", "")
        age = user.get("age")

        if weight < 0.1 or (not bio and not profession and not age):
            return ""

        parts = []
        if weight >= 0.1:
            user_desc = "用户背景："
            if age:
                user_desc += f"{age}岁"
            if profession:
                user_desc += f"，职业是{profession}"
            if bio:
                user_desc += f"。{bio}"
            parts.append(user_desc)

        if weight >= 0.7:
            parts.append("请务必针对用户的身份背景，给出高度相关的个性化建议。")
        elif weight >= 0.4:
            parts.append("可以适当结合用户背景来给出建议。")
        else:
            parts.append("可以偶尔提及用户背景，但以普适性智慧为主。")

        return "\n".join(parts) + "\n\n"

    def _build_avoid_dup_context(self, recent_contents: list[str]) -> str:
        """构建避免重复的提示"""
        if not recent_contents:
            return ""
        samples = recent_contents[-3:]
        joined = "\n".join(f"- {s[:40]}..." for s in samples)
        return f"\n7. 以下是一些近期已生成的内容，请避免与它们重复或过于相似：\n{joined}\n"

    def _build_mentor_prompt(self, keyword: dict, mentor: dict, user: dict, gen_context: dict) -> str:
        """常规导师 Prompt"""
        era_desc = f"生活在{mentor.get('era', '')}，" if mentor.get("era") else ""
        field_desc = f"在{mentor.get('field', '')}领域有深厚造诣。" if mentor.get("field") else "一位智者。"
        field_desc2 = mentor.get("field", "人生") or "人生"

        peak_context = ""
        if mentor.get("peak_stage"):
            peak_context = f"你的人生灵感巅峰时刻：{mentor.get('peak_age', '')}岁时，{mentor.get('peak_stage', '')}。{mentor.get('peak_description', '')}"

        personal_context = self._build_personal_context(user)
        avoid_dup_context = self._build_avoid_dup_context(gen_context.get("recent_contents", []))

        return MENTOR_PROMPT_TEMPLATE.format(
            name=mentor["name"],
            era_desc=era_desc,
            field_desc=field_desc,
            personality=mentor.get("personality", "沉稳睿智"),
            tone=mentor.get("tone", "平和而坚定"),
            peak_context=peak_context,
            personal_context=personal_context,
            keyword=keyword["name"],
            field_desc2=field_desc2,
            min_words=gen_context.get("min_words", 30),
            max_words=gen_context.get("max_words", 100),
            avoid_dup_context=avoid_dup_context,
        )

    def _build_future_self_prompt(self, keyword: dict, mentor: dict, user: dict, gen_context: dict) -> str:
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

        personal_context = self._build_personal_context(user)
        avoid_dup_context = self._build_avoid_dup_context(gen_context.get("recent_contents", []))

        return FUTURE_SELF_PROMPT_TEMPLATE.format(
            years_ahead=years_ahead,
            user_name=user_name,
            future_age=future_age,
            current_stage=current_stage,
            user_age=user_age,
            personal_context=personal_context,
            keyword=keyword["name"],
            min_words=gen_context.get("min_words", 30),
            max_words=gen_context.get("max_words", 100),
            avoid_dup_context=avoid_dup_context,
        )
