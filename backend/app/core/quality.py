"""语录质量校验"""

# AI 拒绝/无关内容的关键词
REFUSAL_PHRASES = [
    "作为AI",
    "我无法提供",
    "我是一名AI",
    "作为人工智能",
    "我不能",
    "我无法",
    "作为一个AI",
    "I cannot",
    "As an AI",
    "I'm unable",
]

# 优质语录的长度范围
MIN_LENGTH = 50
MAX_LENGTH = 100


def validate_quality(content: str) -> bool:
    """校验语录质量。返回 True 表示通过"""
    if not content:
        return False

    length = len(content.strip())
    if length < MIN_LENGTH or length > MAX_LENGTH:
        return False

    # 检查是否包含 AI 拒绝内容
    for phrase in REFUSAL_PHRASES:
        if phrase in content:
            return False

    return True
