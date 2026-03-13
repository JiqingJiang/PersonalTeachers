"""
权重调度算法

根据用户配置的关键词权重，选择每日推送的关键词组合
"""
import random
from typing import List, Dict, Optional
from pathlib import Path
import yaml

from app.models.database import Keyword


class KeywordScheduler:
    """关键词调度器"""

    def __init__(self):
        self._keywords: List[Keyword] = []
        self._keywords_by_quadrant: dict[int, List[Keyword]] = {}
        self._load_keywords()

    def _load_keywords(self):
        """从YAML文件加载关键词数据"""
        data_path = Path(__file__).parent.parent.parent / "data" / "keywords.yaml"

        with open(data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 解析关键词数据
        quadrant_num = 1
        for quadrant_key, quadrant_keywords in data['keywords'].items():
            keywords_list = []

            for kw_dict in quadrant_keywords:
                keyword = Keyword(
                    name=kw_dict['name'],
                    english=kw_dict['english'],
                    category=kw_dict['category'],
                    default_weight=kw_dict['default_weight'],
                    description=kw_dict['description'],
                    mentors_preferred=kw_dict['mentors_preferred'],
                    related_keywords=kw_dict['related_keywords'],
                    quadrant=quadrant_num
                )
                keywords_list.append(keyword)
                self._keywords.append(keyword)

            self._keywords_by_quadrant[quadrant_num] = keywords_list
            quadrant_num += 1

    def get_all_keywords(self) -> List[Keyword]:
        """获取所有关键词"""
        return self._keywords

    def get_keywords_by_quadrant(self, quadrant: int) -> List[Keyword]:
        """获取指定象限的关键词"""
        return self._keywords_by_quadrant.get(quadrant, [])

    def select_keywords(
        self,
        count: int,
        user_weights: Dict[str, float],
        ensure_diversity: bool = True
    ) -> List[str]:
        """
        根据权重选择关键词

        Args:
            count: 选择数量
            user_weights: 用户配置的关键词权重
            ensure_diversity: 是否确保象限多样性

        Returns:
            选中的关键词名称列表
        """
        # 构建关键词权重字典
        weights = {}
        for kw in self._keywords:
            # 用户权重优先，否则使用默认权重
            weight = user_weights.get(kw.name, kw.default_weight)
            weights[kw.name] = weight

        # 如果要求多样性，先确保每个象限至少有一个
        selected = []
        remaining_count = count

        if ensure_diversity and count >= 4:
            # 每个象限选一个
            for quadrant in range(1, 5):
                quadrant_keywords = self.get_keywords_by_quadrant(quadrant)
                quadrant_weights = {
                    kw.name: weights.get(kw.name, 1.0)
                    for kw in quadrant_keywords
                }
                chosen = self._weighted_random_choice(quadrant_weights)
                if chosen:
                    selected.append(chosen)
                    # 降低已选关键词的权重，避免重复
                    weights[chosen] *= 0.1

            remaining_count = count - len(selected)

        # 剩余名额按权重选择
        if remaining_count > 0:
            # 排除已选的
            available_weights = {
                k: v for k, v in weights.items()
                if k not in selected
            }

            for _ in range(remaining_count):
                if not available_weights:
                    break

                chosen = self._weighted_random_choice(available_weights)
                if chosen:
                    selected.append(chosen)
                    # 移除已选的
                    available_weights.pop(chosen, None)

        return selected

    def _weighted_random_choice(self, weights: Dict[str, float]) -> str:
        """
        加权随机选择

        Args:
            weights: 关键词权重字典

        Returns:
            选中的关键词名称
        """
        if not weights:
            return None

        # 计算总权重
        total = sum(weights.values())

        if total == 0:
            return random.choice(list(weights.keys()))

        # 轮盘赌选择
        rand = random.uniform(0, total)
        cumulative = 0.0

        for keyword, weight in weights.items():
            cumulative += weight
            if rand <= cumulative:
                return keyword

        # 兜底
        return list(weights.keys())[-1]

    def get_keyword_info(self, keyword_name: str) -> Optional[Keyword]:
        """获取关键词详细信息"""
        for kw in self._keywords:
            if kw.name == keyword_name:
                return kw
        return None

    def get_quadrant_distribution(self, keyword_names: List[str]) -> Dict[int, int]:
        """
        统计关键词的象限分布

        Args:
            keyword_names: 关键词名称列表

        Returns:
            各象限的关键词数量
        """
        distribution = {1: 0, 2: 0, 3: 0, 4: 0}

        for name in keyword_names:
            kw = self.get_keyword_info(name)
            if kw:
                distribution[kw.quadrant] += 1

        return distribution


# 全局单例
_scheduler: KeywordScheduler = None


def get_keyword_scheduler() -> KeywordScheduler:
    """获取关键词调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = KeywordScheduler()
    return _scheduler
