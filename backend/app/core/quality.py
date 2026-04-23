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

# 默认优质语录的长度范围（当外部不指定时使用）
DEFAULT_MIN_LENGTH = 20
DEFAULT_MAX_LENGTH = 200


def validate_quality(content: str, min_length: int = DEFAULT_MIN_LENGTH, max_length: int = DEFAULT_MAX_LENGTH) -> bool:
    """校验语录质量。返回 True 表示通过"""
    if not content:
        return False

    length = len(content.strip())
    if length < min_length or length > max_length:
        return False

    # 检查是否包含 AI 拒绝内容
    for phrase in REFUSAL_PHRASES:
        if phrase in content:
            return False

    return True
