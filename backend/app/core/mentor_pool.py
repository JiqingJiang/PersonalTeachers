"""导师池：加载、索引、选择

复用 v1 的双索引结构（按类别 + 按关键词）。
"""

import random
from loguru import logger


class MentorPool:
    """导师管理和选择"""

    def __init__(self, mentors: list[dict]):
        """
        Args:
            mentors: 导师列表，每项需含 id, name, category, keywords, personality, tone, background 等
        """
        self._mentors = mentors
        self._by_category: dict[str, list[dict]] = {}
        self._by_keyword: dict[str, list[dict]] = {}

        # 构建索引
        for m in mentors:
            cat = m.get("category", "")
            self._by_category.setdefault(cat, []).append(m)

            for kw in m.get("keywords", []) or []:
                self._by_keyword.setdefault(kw, []).append(m)

    def get_all(self) -> list[dict]:
        return self._mentors

    def get_by_category(self, category: str) -> list[dict]:
        return self._by_category.get(category, [])

    def get_by_keyword(self, keyword_name: str) -> list[dict]:
        return self._by_keyword.get(keyword_name, [])

    def select_mentor_for_keyword(
        self,
        keyword_name: str,
        category_prefs: dict[str, float] | None = None,
        enabled_mentor_ids: set[int] | None = None,
        exclude_ids: set[int] | None = None,
    ) -> dict | None:
        """
        为指定关键词选择导师。

        Args:
            keyword_name: 关键词名
            category_prefs: 类别权重 {"historical": 0.3, "modern": 0.4, ...}
            enabled_mentor_ids: 用户启用的导师 ID 集合（None 表示全部启用）
            exclude_ids: 需要排除的导师 ID
        """
        # 获取匹配关键词的导师
        candidates = self._by_keyword.get(keyword_name, [])

        # 如果没有直接匹配，尝试从所有类别中选
        if not candidates:
            candidates = list(self._mentors)

        # 过滤：仅启用的导师
        if enabled_mentor_ids is not None:
            candidates = [m for m in candidates if m["id"] in enabled_mentor_ids]

        # 过滤：排除已选的
        if exclude_ids:
            candidates = [m for m in candidates if m["id"] not in exclude_ids]

        if not candidates:
            return None

        # 按类别权重加权选择
        if category_prefs:
            weights = []
            for m in candidates:
                w = category_prefs.get(m.get("category", ""), 0.1)
                weights.append(max(w, 0.01))
            return self._weighted_choice(candidates, weights)

        return random.choice(candidates)

    @staticmethod
    def _weighted_choice(items: list[dict], weights: list[float]) -> dict | None:
        if not items:
            return None
        total = sum(weights)
        if total <= 0:
            return items[0]
        r = random.uniform(0, total)
        cumulative = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative:
                return items[i]
        return items[-1]
