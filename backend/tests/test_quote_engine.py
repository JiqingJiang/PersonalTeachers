"""语录引擎测试（mock AI）"""

import pytest
from unittest.mock import AsyncMock, patch

from app.core.quote_engine import QuoteEngine
from app.core.keyword_scheduler import KeywordScheduler
from app.core.mentor_pool import MentorPool
from app.core.quality import validate_quality


# 测试数据
SAMPLE_KEYWORDS = [
    {"id": 1, "name": "健康", "quadrant": 1, "default_weight": 2.0},
    {"id": 2, "name": "金钱", "quadrant": 1, "default_weight": 1.5},
    {"id": 3, "name": "爱", "quadrant": 2, "default_weight": 2.0},
    {"id": 4, "name": "认知", "quadrant": 3, "default_weight": 3.0},
    {"id": 5, "name": "自由", "quadrant": 4, "default_weight": 2.0},
    {"id": 6, "name": "时间", "quadrant": 1, "default_weight": 1.0},
    {"id": 7, "name": "伴侣", "quadrant": 2, "default_weight": 1.5},
    {"id": 8, "name": "执行", "quadrant": 3, "default_weight": 2.0},
]

SAMPLE_MENTORS = [
    {
        "id": 1, "name": "老子", "category": "historical",
        "keywords": ["自由", "认知"], "personality": "超然",
        "tone": "淡然", "background": "道家创始人", "field": "哲学",
        "era": "春秋时期", "peak_stage": "悟道",
    },
    {
        "id": 2, "name": "马斯克", "category": "modern",
        "keywords": ["执行", "金钱"], "personality": "激进",
        "tone": "直接", "background": "特斯拉CEO", "field": "科技",
    },
    {
        "id": 3, "name": "5年后的你", "category": "future_self",
        "keywords": ["认知", "自由"], "personality": "成熟",
        "tone": "温暖", "background": "未来的你", "years_ahead": 5,
    },
]

SAMPLE_USER = {
    "id": 1, "nickname": "测试用户", "age": 24,
    "mentor_category_prefs": {"historical": 0.3, "modern": 0.4, "common": 0.1, "future_self": 0.2},
}

MOCK_MODEL_CONFIGS = [
    {"name": "test-model", "base_url": "http://test", "api_key": "test-key", "model_id": "test"},
]


# --- KeywordScheduler Tests ---

def test_keyword_scheduler_selects_from_all_quadrants():
    """测试关键词选择覆盖4个象限"""
    scheduler = KeywordScheduler()
    selected = scheduler.select_keywords(SAMPLE_KEYWORDS, count=8)

    quadrants_covered = {kw["quadrant"] for kw in selected}
    assert len(quadrants_covered) == 4, f"仅覆盖 {quadrants_covered}"


def test_keyword_scheduler_respects_count():
    """测试选择数量正确"""
    scheduler = KeywordScheduler()
    selected = scheduler.select_keywords(SAMPLE_KEYWORDS, count=5)
    assert len(selected) == 5


def test_keyword_scheduler_respects_user_weights():
    """测试用户权重影响选择"""
    scheduler = KeywordScheduler()
    # 给"认知"极高权重
    user_weights = {4: 100.0}  # keyword id 4 = "认知"
    selected = scheduler.select_keywords(SAMPLE_KEYWORDS, user_weights=user_weights, count=8)

    # "认知"应该被选中
    names = [kw["name"] for kw in selected]
    assert "认知" in names


def test_keyword_scheduler_empty_input():
    """测试空输入"""
    scheduler = KeywordScheduler()
    assert scheduler.select_keywords([], count=5) == []


# --- MentorPool Tests ---

def test_mentor_pool_indexes():
    """测试导师池索引"""
    pool = MentorPool(SAMPLE_MENTORS)

    assert len(pool.get_by_category("historical")) == 1
    assert len(pool.get_by_category("modern")) == 1
    assert len(pool.get_by_keyword("自由")) == 2  # 老子 + 5年后
    assert len(pool.get_by_keyword("执行")) == 1  # 马斯克


def test_mentor_pool_select_for_keyword():
    """测试导师选择"""
    pool = MentorPool(SAMPLE_MENTORS)

    mentor = pool.select_mentor_for_keyword("自由")
    assert mentor is not None
    assert mentor["name"] in ["老子", "5年后的你"]


def test_mentor_pool_respects_enabled():
    """测试仅选择启用的导师"""
    pool = MentorPool(SAMPLE_MENTORS)
    enabled = {1}  # 仅启用老子

    mentor = pool.select_mentor_for_keyword("自由", enabled_mentor_ids=enabled)
    assert mentor is not None
    assert mentor["id"] == 1


def test_mentor_pool_excludes():
    """测试排除已选导师"""
    pool = MentorPool(SAMPLE_MENTORS)

    mentor = pool.select_mentor_for_keyword("自由", exclude_ids={1})
    assert mentor is not None
    assert mentor["id"] != 1


# --- Quality Validation Tests ---

def test_quality_valid():
    assert validate_quality("人生最大的遗憾，不是做了什么，而是没做什么。勇敢地去尝试，即使失败了也比后悔好。" * 2)


def test_quality_too_short():
    assert not validate_quality("太短了")


def test_quality_too_long():
    assert not validate_quality("很长" * 200)


def test_quality_ai_refusal():
    assert not validate_quality("作为AI，我无法提供个人建议。" * 3)


def test_quality_empty():
    assert not validate_quality("")


# --- QuoteEngine Tests ---

@pytest.mark.asyncio
async def test_generate_quotes_for_user():
    """测试完整生成流程（mock AI）"""
    engine = QuoteEngine()

    mock_response = "人生的意义不在于寻找答案，而在于提出正确的问题。每个人都在自己的道路上前行，不必与他人比较。" * 2

    with patch.object(
        engine.fallback_chain, "generate",
        new_callable=AsyncMock,
        return_value=(mock_response, "test-model"),
    ):
        quotes = await engine.generate_quotes_for_user(
            user=SAMPLE_USER,
            keywords=SAMPLE_KEYWORDS,
            mentors=SAMPLE_MENTORS,
            user_keyword_weights=None,
            user_mentor_ids=None,
            model_configs=MOCK_MODEL_CONFIGS,
            count=5,
        )

    assert len(quotes) > 0
    assert all("content" in q for q in quotes)
    assert all("mentor_name" in q for q in quotes)
    assert all("keyword" in q for q in quotes)


@pytest.mark.asyncio
async def test_generate_quotes_no_keywords():
    """测试无关键词时返回空"""
    engine = QuoteEngine()
    quotes = await engine.generate_quotes_for_user(
        user=SAMPLE_USER,
        keywords=[],
        mentors=SAMPLE_MENTORS,
        user_keyword_weights=None,
        user_mentor_ids=None,
        model_configs=MOCK_MODEL_CONFIGS,
        count=5,
    )
    assert quotes == []
