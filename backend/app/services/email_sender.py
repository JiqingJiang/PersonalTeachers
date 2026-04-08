"""邮件发送服务

- send_email(): 单条发送（验证码等场景）
- EmailSenderPool: 多邮箱轮询池（批量推送场景）
"""

import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from loguru import logger

from app.config import get_settings


async def send_email(
    to: str,
    subject: str,
    html_content: str,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
    smtp_username: str | None = None,
    smtp_password: str | None = None,
    max_retries: int = 3,
) -> bool:
    """发送单封邮件（验证码等场景，使用 .env 配置的 SMTP）"""
    settings = get_settings()
    host = smtp_host or settings.SMTP_HOST
    port = smtp_port or settings.SMTP_PORT
    username = smtp_username or settings.SMTP_USERNAME
    password = smtp_password or settings.SMTP_PASSWORD

    if not host or not username:
        logger.warning("SMTP 未配置，跳过邮件发送")
        return False

    message = MIMEMultipart("alternative")
    message["From"] = username
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html", "utf-8"))

    for attempt in range(max_retries):
        try:
            if port == 465:
                await aiosmtplib.send(
                    message, hostname=host, port=port,
                    username=username, password=password, use_tls=True,
                )
            else:
                await aiosmtplib.send(
                    message, hostname=host, port=port,
                    username=username, password=password, start_tls=True,
                )
            logger.info(f"邮件发送成功: {to}")
            return True
        except Exception as e:
            logger.warning(f"邮件发送失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)

    return False


async def send_verification_code_email(to: str, code: str) -> bool:
    """发送验证码邮件"""
    html = f"""
    <div style="max-width:400px;margin:0 auto;font-family:sans-serif;padding:20px;">
        <h2 style="color:#667eea;">PersonalTeachers 验证码</h2>
        <p>您的验证码是：</p>
        <div style="font-size:32px;font-weight:bold;color:#667eea;letter-spacing:8px;text-align:center;padding:20px;background:#f5f5f5;border-radius:8px;">
            {code}
        </div>
        <p style="color:#999;font-size:14px;">验证码5分钟内有效，请勿泄露给他人。</p>
    </div>
    """
    return await send_email(to, "PersonalTeachers 验证码", html)


class EmailSenderPool:
    """多邮箱轮询池，用于批量推送"""

    def __init__(self, senders: list[dict]):
        """
        Args:
            senders: 发件邮箱列表，每项含 email, smtp_host, smtp_port, smtp_password,
                     display_name, daily_limit, sent_today, last_sent_date
        """
        self._senders = senders
        self._current_index = 0

    def get_next_sender(self) -> dict | None:
        """轮询获取下一个可用的发件邮箱"""
        today = _today_str()
        available = []

        for s in self._senders:
            # 重置每日计数器
            if s.get("last_sent_date") != today:
                s["sent_today"] = 0
                s["last_sent_date"] = today

            if s.get("sent_today", 0) < s.get("daily_limit", 200):
                available.append(s)

        if not available:
            logger.error("所有发件邮箱已达到每日发送上限")
            return None

        # round-robin
        sender = available[self._current_index % len(available)]
        self._current_index += 1
        return sender

    async def send_via_pool(self, to: str, subject: str, html_content: str) -> tuple[bool, str]:
        """
        通过邮箱池发送邮件。

        Returns:
            (是否成功, 使用的发件邮箱)
        """
        sender = self.get_next_sender()
        if not sender:
            return False, ""

        success = await send_email(
            to=to,
            subject=subject,
            html_content=html_content,
            smtp_host=sender["smtp_host"],
            smtp_port=sender["smtp_port"],
            smtp_username=sender["email"],
            smtp_password=sender["smtp_password"],
            max_retries=3,
        )

        if success:
            sender["sent_today"] = sender.get("sent_today", 0) + 1

        return success, sender["email"]


def _today_str() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
