"""
定时任务服务

使用APScheduler管理每日语录推送任务
"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time
from typing import Optional
from pathlib import Path
import yaml

from loguru import logger

from app.core import get_quote_engine
from app.services.email_service import get_email_service
from app.models.database import QuoteDB, EmailLogDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DailyQuoteScheduler:
    """每日语录推送调度器"""

    def __init__(self):
        """初始化调度器"""
        self.scheduler = AsyncIOScheduler()
        self.engine = None
        self.Session = None

    def init_database(self):
        """初始化数据库连接"""
        db_path = Path(__file__).parent.parent.parent / "storage" / "quotes.db"
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)

    def start(self, delivery_time: str = "08:00"):
        """
        启动定时任务

        Args:
            delivery_time: 推送时间，格式 "HH:MM"
        """
        # 解析时间
        hour, minute = map(int, delivery_time.split(':'))

        # 添加定时任务
        self.scheduler.add_job(
            self.daily_delivery,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_quote_delivery',
            name='每日语录推送'
        )

        # 启动调度器
        self.scheduler.start()
        logger.info(f"Scheduler started. Daily delivery at {delivery_time}")

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    async def daily_delivery(self):
        """每日推送任务"""
        logger.info("=" * 50)
        logger.info("📧 Starting daily quote delivery...")
        logger.info("=" * 50)

        try:
            # 1. 读取配置
            config = self._load_config()
            user_email = config.get('user', {}).get('email')
            delivery_enabled = config.get('delivery', {}).get('enabled', True)

            if not delivery_enabled:
                logger.info("❌ Delivery is disabled in config")
                return

            if not user_email:
                logger.error("❌ User email not configured")
                return

            # 2. 生成语录
            logger.info("🔄 Generating quotes...")
            engine = get_quote_engine()

            quotes = await engine.generate_quotes(
                count=config.get('generation', {}).get('quote_count', 10),
                keyword_weights=config.get('keyword_weights'),
                mentor_preferences=config.get('mentor_preferences')
            )

            if not quotes:
                logger.error("❌ No quotes generated")
                return

            logger.info(f"✅ Generated {len(quotes)} quotes")

            # 3. 保存到数据库
            self.init_database()
            session = self.Session()

            try:
                for quote in quotes:
                    quote_db = QuoteDB(
                        mentor_name=quote['mentor_name'],
                        mentor_category=quote['mentor_category'],
                        mentor_age=quote.get('mentor_age'),
                        keyword=quote['keyword'],
                        content=quote['content'],
                        ai_model=quote.get('ai_model', 'auto'),
                        created_at=quote.get('created_at', datetime.utcnow())
                    )
                    session.add(quote_db)

                session.commit()
                logger.info("💾 Quotes saved to database")
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Failed to save quotes: {e}")
                return
            finally:
                session.close()

            # 4. 发送邮件
            logger.info("📧 Sending email...")
            email_service = get_email_service()

            date_str = datetime.now().strftime("%Y-%m-%d")
            html_content = email_service.render_daily_quote_email(quotes)

            success = await email_service.send_email(
                to_email=user_email,
                subject=f"📚 今日人生导师智慧 - {date_str}",
                html_content=html_content
            )

            # 5. 记录发送日志
            session = self.Session()
            try:
                log = EmailLogDB(
                    to_email=user_email,
                    subject=f"📚 今日人生导师智慧 - {date_str}",
                    sent_at=datetime.utcnow(),
                    success=1 if success else 0,
                    error_message=None if success else "Failed to send",
                    quote_count=len(quotes)
                )
                session.add(log)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Failed to save email log: {e}")
            finally:
                session.close()

            if success:
                logger.info(f"✅ Email sent successfully to {user_email}")
            else:
                logger.error(f"❌ Failed to send email to {user_email}")

        except Exception as e:
            logger.error(f"❌ Daily delivery failed: {e}")

        logger.info("=" * 50)
        logger.info("✅ Daily delivery completed")
        logger.info("=" * 50)

    def _load_config(self) -> dict:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_next_run_time(self) -> Optional[datetime]:
        """获取下次运行时间"""
        job = self.scheduler.get_job('daily_quote_delivery')
        if job:
            return job.next_run_time
        return None


# 全局单例
_scheduler: Optional[DailyQuoteScheduler] = None


def get_scheduler() -> DailyQuoteScheduler:
    """获取调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = DailyQuoteScheduler()
    return _scheduler
