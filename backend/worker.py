"""RQ Worker 启动入口

独立进程运行: cd backend && python worker.py
"""

import redis
from loguru import logger
from rq import Worker

from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    conn = redis.from_url(settings.REDIS_URL)

    worker = Worker(["push_queue"], connection=conn)
    logger.info("RQ Worker 启动，监听队列: push_queue")
    worker.work()
