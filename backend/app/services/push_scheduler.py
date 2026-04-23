"""定时推送调度器

按时间段分桶调度：不为每个用户创建任务，而是按 push_time 分桶。
推送任务投递到 Redis Queue，由 RQ Worker 异步消费执行。
"""

import asyncio
from datetime import datetime
from loguru import logger
from sqlalchemy import select, and_

from app.models import User, EmailPool, init_db
from app.models import database as db_module
from app.services.cleanup import cleanup_expired_data


class PushScheduler:
    """推送调度器"""

    def __init__(self):
        self._scheduler = None

    def start(self):
        """启动调度器"""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        self._scheduler = AsyncIOScheduler()

        # 每6小时刷新一次时间段任务
        self._scheduler.add_job(
            self._refresh_time_slots, "cron", hour="0,6,12,18", id="refresh_slots"
        )

        # 每天 00:05 重置邮箱池计数
        self._scheduler.add_job(
            self._reset_email_pool, "cron", hour=0, minute=5, id="reset_email_pool"
        )

        # 每天 03:00 清理过期数据
        self._scheduler.add_job(
            cleanup_expired_data, "cron", hour=3, id="cleanup"
        )

        # 初始加载时间段
        self._scheduler.add_job(
            self._refresh_time_slots, id="initial_slots"
        )

        self._scheduler.start()
        logger.info("推送调度器已启动（队列模式）")

    def stop(self):
        if self._scheduler:
            self._scheduler.shutdown()
        logger.info("推送调度器已停止")

    def refresh(self):
        """立即刷新时间段任务（用户修改 push_time 后调用）"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.add_job(self._refresh_time_slots, id="manual_refresh")
            logger.info("手动刷新调度器时间段")

    async def _refresh_time_slots(self):
        """查询所有活跃用户的 push_time，为每个时间段注册 cron 任务"""
        if db_module.async_session is None:
            await init_db()

        async with db_module.async_session() as db:
            result = await db.execute(
                select(User.push_time)
                .where(User.push_enabled == True, User.is_active == True)
                .distinct()
            )
            push_times = [row[0] for row in result.all()]

        # 移除旧的推送任务
        if self._scheduler:
            for job in self._scheduler.get_jobs():
                if job.id.startswith("push_slot_"):
                    self._scheduler.remove_job(job.id)

        # 为每个时间段注册任务
        for pt in push_times:
            try:
                hour, minute = pt.split(":")
                job_id = f"push_slot_{hour}_{minute}"
                self._scheduler.add_job(
                    self._enqueue_for_time_slot,
                    "cron",
                    hour=int(hour),
                    minute=int(minute),
                    id=job_id,
                    args=[pt],
                )
                logger.info(f"注册推送任务: {pt}")
            except Exception as e:
                logger.error(f"注册推送任务失败 {pt}: {e}")

        logger.info(f"已注册 {len(push_times)} 个推送时间段")

    async def _enqueue_for_time_slot(self, push_time: str):
        """将某个时间段需要推送的用户投递到 Redis Queue"""
        if db_module.async_session is None:
            await init_db()

        logger.info(f"开始入队时间段: {push_time}")

        async with db_module.async_session() as db:
            today = datetime.now().strftime("%Y-%m-%d")
            result = await db.execute(
                select(User).where(
                    and_(
                        User.push_time == push_time,
                        User.push_enabled == True,
                        User.is_active == True,
                        (User.last_push_date != today) | (User.last_push_date == None),
                    )
                )
            )
            users = result.scalars().all()

        if not users:
            logger.info(f"时间段 {push_time}: 无需推送的用户")
            return

        from app.services.push_queue import enqueue_push

        for user in users:
            enqueue_push(user.id)

        logger.info(f"时间段 {push_time}: 已入队 {len(users)} 个用户")

    async def _reset_email_pool(self):
        """重置邮箱池每日计数"""
        if db_module.async_session is None:
            return

        async with db_module.async_session() as db:
            result = await db.execute(select(EmailPool).where(EmailPool.is_active == True))
            for sender in result.scalars().all():
                sender.sent_today = 0
                sender.last_sent_date = None
            await db.commit()

        logger.info("邮箱池每日计数已重置")
