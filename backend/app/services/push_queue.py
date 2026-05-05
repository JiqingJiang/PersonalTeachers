"""推送任务队列管理：封装 RQ 入队逻辑"""

import redis as redis_lib
from rq import Queue, Retry

from app.config import get_settings

_redis_conn = None


def _get_redis_conn():
    """复用 Redis 连接，避免每次入队创建新 TCP 连接"""
    global _redis_conn
    if _redis_conn is None:
        settings = get_settings()
        _redis_conn = redis_lib.from_url(settings.REDIS_URL)
    return _redis_conn


def enqueue_push(user_id: int) -> None:
    """将单个用户的推送任务投递到队列"""
    queue = Queue("push_queue", connection=_get_redis_conn())
    queue.enqueue(
        "app.services.push_worker.execute_push",
        user_id=user_id,
        job_timeout=120,
        retry=Retry(
            max=3,
            interval=[60, 300, 900],
        ),
    )
