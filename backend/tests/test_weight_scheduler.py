"""
权重调度算法单元测试
测试关键词选择算法的权重分配和多样性保证
"""
import pytest
from app.core.weight_scheduler import WeightScheduler


@pytest.fixture
def scheduler():
    """创建权重调度器实例"""
    return WeightScheduler()


@pytest.fixture
def sample_keywords():
    """示例关键词数据"""
    return {
        "健康": {"quadrant": 1, "default_weight": 2.0},
        "金钱": {"quadrant": 1, "default_weight": 1.0},
        "爱": {"quadrant": 2, "default_weight": 1.0},
        "友情": {"quadrant": 2, "default_weight": 1.0},
        "选择": {"quadrant": 3, "default_weight": 1.0},
        "学习": {"quadrant": 3, "default_weight": 1.0},
        "自由": {"quadrant": 4, "default_weight": 1.0},
        "真理": {"quadrant": 4, "default_weight": 1.0}
    }


class TestWeightScheduler:
    """权重调度器测试类"""

    def test_weighted_selection(self, scheduler, sample_keywords):
        """测试加权随机选择：高权重关键词应更频繁出现"""
        # 设置极端权重
        user_weights = {
            "健康": 10.0,
            "金钱": 0.1,
            "爱": 0.1,
            "友情": 0.1,
            "选择": 0.1,
            "学习": 0.1,
            "自由": 0.1,
            "真理": 0.1
        }

        # 初始化调度器
        scheduler.load_keywords(sample_keywords)

        # 选择100次，统计"健康"出现频率
        health_count = 0
        selections = 100

        for _ in range(selections):
            selected = scheduler.select_keywords(count=1, user_weights=user_weights, ensure_diversity=False)
            if selected and selected[0] == "健康":
                health_count += 1

        health_ratio = health_count / selections

        # "健康"应该占主导（至少50%）
        assert health_ratio > 0.5, f"Expected '健康' to appear >50% of the time, got {health_ratio:.2%}"

    def test_diversity_guarantee(self, scheduler, sample_keywords):
        """测试多样性保证：选择>=4个时，每个象限至少出现一次"""
        user_weights = {k: 1.0 for k in sample_keywords.keys()}

        scheduler.load_keywords(sample_keywords)

        # 选择8个关键词（>=4，应保证多样性）
        selected = scheduler.select_keywords(count=8, user_weights=user_weights, ensure_diversity=True)

        # 验证每个象限至少出现一次
        quadrants = {1: False, 2: False, 3: False, 4: False}
        for keyword in selected:
            quadrant = sample_keywords[keyword]["quadrant"]
            quadrants[quadrant] = True

        assert all(quadrants.values()), f"Not all quadrants represented: {quadrants}"

    def test_equal_weights_distribution(self, scheduler, sample_keywords):
        """测试等权重分布：所有权重相等时，分布应相对均匀"""
        user_weights = {k: 1.0 for k in sample_keywords.keys()}

        scheduler.load_keywords(sample_keywords)

        # 选择100次，统计分布
        counts = {k: 0 for k in sample_keywords.keys()}
        iterations = 100

        for _ in range(iterations):
            selected = scheduler.select_keywords(count=1, user_weights=user_weights, ensure_diversity=False)
            if selected:
                counts[selected[0]] += 1

        # 每个关键词出现次数应在5-20次之间（相对均匀）
        for keyword, count in counts.items():
            assert 5 <= count <= 20, f"{keyword} appeared {count} times, expected 5-20"

    def test_count_parameter(self, scheduler, sample_keywords):
        """测试count参数：返回数量应匹配请求"""
        user_weights = {k: 1.0 for k in sample_keywords.keys()}

        scheduler.load_keywords(sample_keywords)

        for count in [1, 3, 5, 10]:
            selected = scheduler.select_keywords(count=count, user_weights=user_weights)
            assert len(selected) == count, f"Expected {count} keywords, got {len(selected)}"

    def test_default_weights(self, scheduler, sample_keywords):
        """测试默认权重：未指定的关键词应使用默认权重"""
        # 只指定一个关键词的权重
        user_weights = {"健康": 5.0}

        scheduler.load_keywords(sample_keywords)

        # 选择多次，验证"健康"出现频率高
        health_count = 0
        iterations = 50

        for _ in range(iterations):
            selected = scheduler.select_keywords(count=1, user_weights=user_weights, ensure_diversity=False)
            if selected and selected[0] == "健康":
                health_count += 1

        health_ratio = health_count / iterations

        # "健康"应该更频繁（至少30%）
        assert health_ratio > 0.3, f"Expected '健康' to appear >30% with high weight, got {health_ratio:.2%}"

    def test_empty_keywords(self, scheduler):
        """测试空关键词列表"""
        scheduler.load_keywords({})

        selected = scheduler.select_keywords(count=5, user_weights={}, ensure_diversity=False)

        assert selected == [], "Expected empty list for empty keywords"

    def test_fallback_to_default_weight(self, scheduler, sample_keywords):
        """测试回退到默认权重"""
        # 用户权重不包含某些关键词
        user_weights = {"健康": 2.0}  # 只有"健康"有权重

        scheduler.load_keywords(sample_keywords)

        # 选择多个关键词，应能正常工作（其他关键词使用默认权重）
        selected = scheduler.select_keywords(count=5, user_weights=user_weights, ensure_diversity=True)

        assert len(selected) == 5, f"Expected 5 keywords, got {len(selected)}"
        assert all(k in sample_keywords for k in selected), "Selected keyword not in sample keywords"


@pytest.mark.parametrize("count,quadrants_count", [
    (1, 1),    # 1个关键词
    (3, 3),    # 3个关键词
    (4, 4),    # 4个关键词（开始保证多样性）
    (8, 4),    # 8个关键词
    (12, 4),   # 12个关键词
])
def test_quadrant_coverage(scheduler, sample_keywords, count, quadrants_count):
    """参数化测试：不同数量选择时的象限覆盖"""
    user_weights = {k: 1.0 for k in sample_keywords.keys()}
    scheduler.load_keywords(sample_keywords)

    selected = scheduler.select_keywords(count=count, user_weights=user_weights, ensure_diversity=True)

    # 基本验证
    assert len(selected) == count

    # 如果count>=4，验证所有象限都被覆盖
    if count >= 4:
        quadrants = set()
        for keyword in selected:
            quadrants.add(sample_keywords[keyword]["quadrant"])
        assert len(quadrants) == 4, f"Expected all 4 quadrants for count={count}, got {len(quadrants)}"
