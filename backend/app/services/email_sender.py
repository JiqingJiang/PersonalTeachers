"""邮件发送服务

- send_email(): 单条发送（验证码等场景）
- EmailSenderPool: 多邮箱轮询池（批量推送场景）
"""

import asyncio
import random
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
) -> tuple[bool, str]:
    """发送单封邮件（验证码等场景，使用 .env 配置的 SMTP）

    Returns:
        (是否成功, 错误信息，成功时为空字符串)
    """
    settings = get_settings()
    host = smtp_host or settings.SMTP_HOST
    port = smtp_port or settings.SMTP_PORT
    username = smtp_username or settings.SMTP_USERNAME
    password = smtp_password or settings.SMTP_PASSWORD

    if not host or not username:
        msg = "SMTP 未配置，跳过邮件发送"
        logger.warning(msg)
        return False, msg

    message = MIMEMultipart("alternative")
    message["From"] = username
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html", "utf-8"))

    last_error = ""
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
            return True, ""
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            logger.warning(f"邮件发送失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)

    return False, last_error


async def send_verification_code_email(to: str, code: str) -> bool:
    """发送验证码邮件"""
    html = f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#F8F4EE;">
    <tr><td align="center" style="padding:32px 16px;">
    <table role="presentation" width="400" cellpadding="0" cellspacing="0" border="0" style="max-width:400px; width:100%; border-radius:12px; overflow:hidden; box-shadow:0 2px 20px rgba(45,43,38,0.06);">
        <!-- Header -->
        <tr><td style="background:linear-gradient(135deg,#E8A838 0%,#D4763C 50%,#B8533A 100%); padding:32px; text-align:center; border-radius:12px 12px 0 0;">
            <p style="margin:0; font-family:Georgia,'Times New Roman',serif; font-size:18px; color:#FFFFFF; font-weight:700; letter-spacing:1px;">PersonalTeachers</p>
            <p style="margin:6px 0 0; font-size:12px; color:rgba(255,255,255,0.85);">验证码</p>
        </td></tr>
        <!-- Code -->
        <tr><td style="background-color:#FFFFFF; padding:36px 32px;">
            <p style="margin:0 0 24px; font-size:14px; color:#7A756A; text-align:center;">您的验证码是：</p>
            <div style="font-size:36px; font-weight:700; color:#D4763C; letter-spacing:12px; text-align:center; padding:24px 20px; background:#FAF7F2; border-radius:10px; border:2px dashed #EDE8DF; font-family:'Courier New',monospace;">{code}</div>
            <p style="margin:16px 0 0; font-size:12px; color:#9A9488; text-align:center;">验证码 5 分钟内有效，请勿泄露给他人。</p>
        </td></tr>
        <!-- Footer -->
        <tr><td style="background-color:#FAF7F2; padding:16px 32px 20px; border-radius:0 0 12px 12px;">
            <p style="margin:0; font-size:11px; color:#B5AFA3; text-align:center;">PersonalTeachers &mdash; 每日人生智慧推送</p>
        </td></tr>
    </table>
    </td></tr>
    </table>
    """
    success, _ = await send_email(to, "PersonalTeachers 验证码", html)
    return success


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

    async def send_via_pool(self, to: str, subject: str, html_content: str) -> tuple[bool, str, str]:
        """
        通过邮箱池发送邮件。

        Returns:
            (是否成功, 使用的发件邮箱, 错误信息)
        """
        sender = self.get_next_sender()
        if not sender:
            return False, "", "邮箱池无可用发件邮箱"

        # 发送前随机延迟 1.5~4 秒，避免 SMTP 限流
        delay = random.uniform(1.5, 4.0)
        await asyncio.sleep(delay)

        success, error = await send_email(
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

        return success, sender["email"], error


def _today_str() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")
