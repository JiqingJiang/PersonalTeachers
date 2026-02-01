"""
邮件发送服务

负责发送每日语录推送邮件
"""
import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from loguru import logger


class EmailService:
    """邮件发送服务"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        from_name: str = "PersonalTeachers"
    ):
        """
        初始化邮件服务

        Args:
            host: SMTP服务器地址
            port: SMTP端口
            username: 邮箱账号
            password: 邮箱密码
            from_email: 发件人邮箱
            from_name: 发件人名称
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.from_name = from_name

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        max_retries: int = 3
    ) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            max_retries: 最大重试次数

        Returns:
            是否发送成功
        """
        # 参数验证
        if not to_email:
            logger.error("to_email is None or empty")
            return False
        if not subject:
            logger.error("subject is None or empty")
            return False
        if not html_content:
            logger.error("html_content is None or empty")
            return False

        logger.debug(f"Preparing email: to={to_email}, subject={subject[:50]}, html_len={len(html_content)}")

        for attempt in range(max_retries):
            try:
                # 创建邮件
                message = MIMEMultipart('alternative')
                message['Subject'] = Header(str(subject), 'utf-8')  # 确保是字符串
                message['From'] = f"{self.from_name} <{self.from_email}>"
                message['To'] = str(to_email)  # 确保是字符串

                # 添加HTML内容
                html_part = MIMEText(str(html_content), 'html', 'utf-8')  # 确保是字符串
                message.attach(html_part)

                # 发送邮件
                # 587端口使用STARTTLS，465端口使用SSL
                use_tls = (self.port == 465)
                async with aiosmtplib.SMTP(
                    hostname=self.host,
                    port=self.port,
                    use_tls=use_tls,
                    start_tls=(self.port == 587)
                ) as smtp:
                    await smtp.login(self.username, self.password)
                    await smtp.send_message(message)

                logger.info(f"Email sent successfully to {to_email}")
                return True

            except Exception as e:
                logger.warning(f"Email send attempt {attempt + 1} failed: {type(e).__name__}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to send email after {max_retries} attempts. Last error: {type(e).__name__}: {e}")
                    return False
                await asyncio.sleep(1)

        return False

    def render_daily_quote_email(
        self,
        quotes: List[Dict],
        date: Optional[datetime] = None
    ) -> str:
        """
        渲染每日语录邮件模板

        Args:
            quotes: 语录列表
            date: 日期（默认为今天）

        Returns:
            HTML内容
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d")

        # 统计象限分布
        quadrant_count = {"1": 0, "2": 0, "3": 0, "4": 0}
        quadrant_names = {
            "1": "生存",
            "2": "情感",
            "3": "成长",
            "4": "哲思"
        }

        for quote in quotes:
            keyword_info = self._get_keyword_quadrant(quote['keyword'])
            if keyword_info:
                quadrant_count[str(keyword_info)] += 1

        # 生成语录列表HTML
        quotes_html = ""
        for i, quote in enumerate(quotes, 1):
            emoji = self._get_emoji_for_number(i)
            quotes_html += f"""
            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">
                <div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">
                    {emoji} 【{quote['keyword']}】 · {quote['mentor_name']}
                </div>
                <div style="font-size: 15px; line-height: 1.6; color: #212529;">
                    {quote['content']}
                </div>
            </div>
            """

        # 生成象限分布HTML
        distribution_html = ""
        for q in ["1", "2", "3", "4"]:
            emoji = {"1": "🟢", "2": "🔵", "3": "🟡", "4": "🟣"}[q]
            distribution_html += f"{emoji} {quadrant_names[q]}：{quadrant_count[q]}条  "

        # 读取邮件模板
        template_path = Path(__file__).parent.parent.parent / "templates" / "daily_quote.html"

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            # 如果模板文件不存在，使用简单的HTML
            template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }
        .content { background: #fff; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 今日人生导师智慧</h1>
            <p style="margin: 0; opacity: 0.9;">{{date_str}}</p>
        </div>
        <div class="content">
            {{quotes_html}}
            <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">
            <p style="font-size: 14px; color: #6c757d;">
                🎯 本日主题分布：<br>
                {{distribution_html}}
            </p>
        </div>
        <div class="footer">
            <p>💡 管理你的偏好 | 📚 查看历史语录</p>
            <p style="margin: 5px 0 0 0;">— Powered by PersonalTeachers —</p>
        </div>
    </div>
</body>
</html>
            """

        # 填充模板
        html = template.replace("{{date_str}}", date_str)
        html = html.replace("{{quotes_html}}", quotes_html)
        html = html.replace("{{distribution_html}}", distribution_html)

        return html

    def _get_keyword_quadrant(self, keyword_name: str) -> Optional[int]:
        """获取关键词所属象限"""
        # 这里简化处理，实际应该从数据中查询
        quadrant_1 = ["健康", "金钱", "时间", "睡眠", "房子", "欲望", "性", "衰老", "风险", "安全感", "债务", "食物", "贫穷", "生存", "资产"]
        quadrant_2 = ["爱", "父母", "伴侣", "孤独", "信任", "遗憾", "嫉妒", "面子", "归属感", "告别", "尊重", "情绪", "原谅", "朋友", "孩子"]
        quadrant_3 = ["选择", "认知", "习惯", "复利", "专注", "学习", "失败", "逻辑", "改变", "耐心", "焦虑", "竞争", "天赋", "执行", "阶层"]
        quadrant_4 = ["自由", "意义", "死亡", "命运", "真理", "自我", "遗忘", "权力", "公平", "无常", "创造", "责任", "和解", "信仰", "因果"]

        if keyword_name in quadrant_1:
            return 1
        elif keyword_name in quadrant_2:
            return 2
        elif keyword_name in quadrant_3:
            return 3
        elif keyword_name in quadrant_4:
            return 4
        return None

    def _get_emoji_for_number(self, num: int) -> str:
        """获取数字对应的emoji"""
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        return emojis[num - 1] if num <= 10 else f"#{num}"


# 全局单例
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """获取邮件服务单例"""
    global _email_service
    if _email_service is None:
        import os
        from dotenv import load_dotenv
        # 确保加载环境变量
        load_dotenv()
        _email_service = EmailService(
            host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            from_email=os.getenv("EMAIL_FROM"),
            from_name=os.getenv("EMAIL_FROM_NAME", "PersonalTeachers")
        )
    return _email_service
