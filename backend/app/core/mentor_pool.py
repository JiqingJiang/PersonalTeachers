"""
导师池管理

负责加载和管理50位导师的数据
"""
import yaml
import random
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from app.models.database import Mentor, MentorCategory, Perspective


@dataclass
class MentorData:
    """导师数据容器"""
    mentors: List[Mentor]
    by_category: dict[MentorCategory, List[Mentor]]
    by_keyword: dict[str, List[Mentor]]

    def get_mentors_by_category(self, category: MentorCategory) -> List[Mentor]:
        """根据类别获取导师列表"""
        return self.by_category.get(category, [])

    def get_mentors_by_keyword(self, keyword: str) -> List[Mentor]:
        """根据关键词获取导师列表"""
        return self.by_keyword.get(keyword, [])

    def get_random_mentor(
        self,
        category: Optional[MentorCategory] = None,
        keyword: Optional[str] = None,
        exclude_ids: Optional[set[str]] = None
    ) -> Optional[Mentor]:
        """
        获取随机导师

        Args:
            category: 限定类别
            keyword: 限定关键词
            exclude_ids: 排除的导师ID

        Returns:
            随机导师实例
        """
        candidates = []

        if category and keyword:
            # 同时匹配类别和关键词
            category_mentors = self.get_mentors_by_category(category)
            keyword_mentors = self.get_mentors_by_keyword(keyword)
            candidates = [m for m in category_mentors if m in keyword_mentors]

        elif category:
            candidates = self.get_mentors_by_category(category)

        elif keyword:
            candidates = self.get_mentors_by_keyword(keyword)

        else:
            candidates = self.mentors

        # 排除指定ID
        if exclude_ids:
            candidates = [m for m in candidates if m.id not in exclude_ids]

        return random.choice(candidates) if candidates else None


class MentorPool:
    """导师池管理器（单例）"""

    _instance: Optional['MentorPool'] = None
    _data: Optional[MentorData] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._data is None:
            self._load_mentors()

    def _load_mentors(self):
        """从YAML文件加载导师数据"""
        data_path = Path(__file__).parent.parent.parent / "data" / "mentors.yaml"

        with open(data_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 解析导师数据
        mentors = []
        by_category = {cat: [] for cat in MentorCategory}
        by_keyword = {}

        for category_str, category_mentors in data['mentors'].items():
            category = MentorCategory(category_str)

            for mentor_dict in category_mentors:
                mentor = Mentor(
                    id=mentor_dict['id'],
                    name=mentor_dict['name'],
                    category=MentorCategory(mentor_dict['category']),
                    age_range=tuple(mentor_dict['age_range']),
                    field=mentor_dict['field'],
                    perspective=Perspective(mentor_dict['perspective']),
                    keywords=mentor_dict['keywords'],
                    personality=mentor_dict['personality'],
                    tone=mentor_dict['tone'],
                    background=mentor_dict['background'],
                    era=mentor_dict.get('era'),
                    achievements=mentor_dict.get('achievements'),
                    template_type=mentor_dict.get('template_type'),
                    years_ahead=mentor_dict.get('years_ahead')
                )

                mentors.append(mentor)
                by_category[category].append(mentor)

                # 按关键词索引
                for keyword in mentor.keywords:
                    if keyword not in by_keyword:
                        by_keyword[keyword] = []
                    by_keyword[keyword].append(mentor)

        self._data = MentorData(
            mentors=mentors,
            by_category=by_category,
            by_keyword=by_keyword
        )

    @property
    def data(self) -> MentorData:
        """获取导师数据"""
        return self._data

    def get_all_mentors(self) -> List[Mentor]:
        """获取所有导师"""
        return self._data.mentors

    def get_mentor_by_id(self, mentor_id: str) -> Optional[Mentor]:
        """根据ID获取导师"""
        for mentor in self._data.mentors:
            if mentor.id == mentor_id:
                return mentor
        return None

    def get_mentors_by_category(self, category: MentorCategory) -> List[Mentor]:
        """根据类别获取导师"""
        return self._data.get_mentors_by_category(category)

    def get_mentors_by_keyword(self, keyword: str) -> List[Mentor]:
        """根据关键词获取导师"""
        return self._data.get_mentors_by_keyword(keyword)

    def select_mentor_for_keyword(
        self,
        keyword: str,
        category_preferences: dict[str, float],
        exclude_recent: Optional[set[str]] = None,
        age_diversity: bool = True
    ) -> Mentor:
        """
        为关键词选择合适的导师

        Args:
            keyword: 关键词
            category_preferences: 类别偏好权重 {"historical": 0.3, ...}
            exclude_recent: 排除最近使用的导师ID
            age_diversity: 是否考虑年龄多样性

        Returns:
            选中的导师
        """
        # 获取该关键词的所有候选导师
        candidates = self.get_mentors_by_keyword(keyword)

        if not candidates:
            # 如果没有候选导师，从所有导师中随机选
            candidates = self.get_all_mentors()

        # 按类别偏好加权
        scored_mentors = []
        for mentor in candidates:
            base_score = random.random()

            # 应用类别偏好
            category_weight = category_preferences.get(mentor.category.value, 0.25)
            final_score = base_score * (1 + category_weight * 2)

            scored_mentors.append((mentor, final_score))

        # 排除最近使用过的
        if exclude_recent:
            scored_mentors = [
                (m, s) for m, s in scored_mentors
                if m.id not in exclude_recent
            ]

        # 按分数排序并选择
        scored_mentors.sort(key=lambda x: x[1], reverse=True)
        return scored_mentors[0][0] if scored_mentors else candidates[0]

    def reload(self):
        """重新加载导师数据"""
        self._load_mentors()


# 全局单例
_mentor_pool: Optional[MentorPool] = None


def get_mentor_pool() -> MentorPool:
    """获取导师池单例"""
    global _mentor_pool
    if _mentor_pool is None:
        _mentor_pool = MentorPool()
    return _mentor_pool
