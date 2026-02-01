"""
关键词相关API端点
"""
from fastapi import APIRouter
from typing import Dict
from pathlib import Path
import yaml

router = APIRouter(prefix="/api/keywords", tags=["关键词"])


@router.get("")
async def get_keywords() -> Dict:
    """
    获取所有关键词分类

    返回60个关键词，按4个象限分类
    """
    keywords_path = Path(__file__).parent.parent.parent / "data" / "keywords.yaml"

    with open(keywords_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    return data.get("keywords", {})
