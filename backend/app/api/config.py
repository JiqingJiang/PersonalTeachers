"""
配置相关API端点

提供配置读取、更新等功能
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from pathlib import Path
import yaml
from loguru import logger
from pydantic import BaseModel


router = APIRouter(prefix="/api/config", tags=["配置"])


class ConfigRequest(BaseModel):
    """配置请求模型（嵌套结构）"""
    user: Optional[Dict] = None
    delivery: Optional[Dict] = None
    quote_count: Optional[int] = None
    ai_model: Optional[Dict] = None
    mentor_preferences: Optional[Dict] = None
    keyword_weights: Optional[Dict] = None


@router.get("")
async def get_config():
    """
    获取当前配置（返回嵌套结构，与前端保持一致）
    """
    try:
        config = _load_config()

        # 返回嵌套结构，与前端期望的格式一致
        return {
            "user": config.get('user', {
                "name": "",
                "age": 26,
                "profession": "",
                "email": ""
            }),
            "delivery": config.get('delivery', {
                "time": "08:00",
                "enabled": True
            }),
            "quote_count": config.get('generation', {}).get('quote_count', 10),
            "ai_model": config.get('ai_model', {
                "primary": "auto",
                "fallback_order": ["glm", "deepseek", "minimax"]
            }),
            "mentor_preferences": config.get('mentor_preferences', {
                "historical": 0.3,
                "modern": 0.4,
                "future_self": 0.2,
                "common": 0.1
            }),
            "keyword_weights": config.get('keyword_weights', {})
        }

    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_config(update: ConfigRequest):
    """
    更新配置

    支持更新关键词权重、推送时间、AI模型等
    """
    try:
        # 加载当前配置
        config = _load_config()
        config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

        # 追踪是否需要重启调度器
        need_restart_scheduler = False

        # 更新用户信息
        if update.user is not None:
            if 'name' in update.user:
                config['user']['name'] = update.user['name']
            if 'age' in update.user:
                config['user']['age'] = update.user['age']
            if 'profession' in update.user:
                config['user']['profession'] = update.user['profession']
            if 'email' in update.user:
                config['user']['email'] = update.user['email']

        # 更新推送设置
        if update.delivery is not None:
            if 'time' in update.delivery:
                if config['delivery'].get('time') != update.delivery['time']:
                    need_restart_scheduler = True
                config['delivery']['time'] = update.delivery['time']
            if 'enabled' in update.delivery:
                if config['delivery'].get('enabled') != update.delivery['enabled']:
                    need_restart_scheduler = True
                config['delivery']['enabled'] = update.delivery['enabled']

        # 更新语录数量
        if update.quote_count is not None:
            if 'generation' not in config:
                config['generation'] = {}
            config['generation']['quote_count'] = update.quote_count

        # 更新AI模型设置
        if update.ai_model is not None:
            if 'primary' in update.ai_model:
                config['ai_model']['primary'] = update.ai_model['primary']
            if 'fallback_order' in update.ai_model:
                config['ai_model']['fallback_order'] = update.ai_model['fallback_order']

        # 更新导师偏好
        if update.mentor_preferences is not None:
            config['mentor_preferences'].update(update.mentor_preferences)

        # 更新关键词权重
        if update.keyword_weights is not None:
            if 'keyword_weights' not in config:
                config['keyword_weights'] = {}
            config['keyword_weights'].update(update.keyword_weights)

        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)

        logger.info("Config updated successfully")

        # 如果推送时间或启用状态改变，重启调度器
        if need_restart_scheduler:
            from app.services import get_scheduler
            scheduler = get_scheduler()
            scheduler.stop()
            delivery_time = config['delivery'].get('time', '08:00')
            delivery_enabled = config['delivery'].get('enabled', True)
            if delivery_enabled:
                scheduler.init_database()
                scheduler.start(delivery_time)
                logger.info(f"Scheduler restarted with new time: {delivery_time}")
            else:
                logger.info("Scheduler disabled")

        return {"message": "配置已更新" + ("，调度器已重启" if need_restart_scheduler else "")}

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_config():
    """
    重新加载配置

    重启系统后需要调用此接口
    """
    try:
        from app.core import get_mentor_pool, get_keyword_scheduler, get_quote_engine

        # 重新加载配置
        get_mentor_pool().reload()
        logger.info("Mentor pool reloaded")

        # 清空单例缓存（如果实现了的话）
        # 这样下次获取时会重新加载

        return {"message": "配置已重新加载"}

    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
