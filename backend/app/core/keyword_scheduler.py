"""关键词权重调度器

从关键词库中按权重随机选择，保证4象限多样性。
复用 v1 的核心算法。
"""

import random
from loguru import logger


class KeywordScheduler:
    """关键词选择器：加权随机 + 象限多样性保证"""

    def select_keywords(
        self,
        keywords: list[dict],
        user_weights: dict[int, float] | None = None,
        count: int = 10,
    ) -> list[dict]:
        """
        选择关键词，保证象限多样性。

        Args:
            keywords: 所有关键词列表，每项需含 id, name, quadrant, default_weight
            user_weights: 用户自定义权重 {keyword_id: weight}
            count: 需要选择的数量

        Returns:
            选中的关键词列表
        """
        if not keywords:
            return []

        if user_weights is None:
            user_weights = {}

        # 按象限分组
        quadrants: dict[int, list[dict]] = {}
        for kw in keywords:
            q = kw.get("quadrant", 1)
            quadrants.setdefault(q, []).append(kw)

        selected = []

        # 阶段1：保证每个象限至少选一个（如果 count >= 4）
        if count >= 4:
            for q in range(1, 5):
                if q in quadrants and quadrants[q]:
                    chosen = self._weighted_choice(quadrants[q], user_weights)
                    if chosen:
                        selected.append(chosen)

        # 阶段2：剩余名额按全局权重填充
        remaining = count - len(selected)
        if remaining > 0:
            # 排除已选的
            selected_ids = {kw["id"] for kw in selected}
            candidates = [kw for kw in keywords if kw["id"] not in selected_ids]

            for _ in range(remaining):
                if not candidates:
                    break
                chosen = self._weighted_choice(candidates, user_weights)
                if chosen:
                    selected.append(chosen)
                    candidates = [kw for kw in candidates if kw["id"] != chosen["id"]]

        return selected

    def _weighted_choice(self, keywords: list[dict], user_weights: dict[int, float]) -> dict | None:
        """加权随机选择一个关键词"""
        if not keywords:
            return None

        weights = []
        for kw in keywords:
            w = user_weights.get(kw["id"], kw.get("default_weight", 1.0))
            weights.append(max(w, 0.01))  # 最小权重防止全零

        total = sum(weights)
        if total <= 0:
            return keywords[0]

        r = random.uniform(0, total)
        cumulative = 0
        for i, w in enumerate(weights):
            cumulative += w
            if r <= cumulative:
                return keywords[i]

        return keywords[-1]
