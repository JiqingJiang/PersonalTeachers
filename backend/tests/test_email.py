"""
邮件服务测试
测试邮件发送功能和HTML模板渲染
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.email_service import EmailService
from datetime import datetime


# 测试邮件配置
TEST_SMTP_CONFIG = {
    "host": "smtp.example.com",
    "port": 587,
    "username": "test@example.com",
    "password": "test_password",
    "from_email": "noreply@example.com",
    "from_name": "PersonalTeachers"
}


class TestEmailService:
    """邮件服务测试"""

    @pytest.fixture
    def email_service(self):
        """创建邮件服务实例"""
        return EmailService(**TEST_SMTP_CONFIG)

    @pytest.fixture
    def sample_quotes(self):
        """示例语录数据"""
        return [
            {
                "id": 1,
                "keyword": "健康",
                "mentor_name": "钟南山",
                "mentor_category": "modern",
                "content": "健康是1，其他都是0。没有健康，一切都没有意义。",
                "created_at": "2026-01-17T08:00:00"
            },
            {
                "id": 2,
                "keyword": "选择",
                "mentor_name": "巴菲特",
                "mentor_category": "modern",
                "content": "人生中最重要的选择，是选择与谁为伍。",
                "created_at": "2026-01-17T08:00:00"
            },
            {
                "id": 3,
                "keyword": "自由",
                "mentor_name": "老子",
                "mentor_category": "historical",
                "content": "知足不辱，知止不殆，可以长久。",
                "created_at": "2026-01-17T08:00:00"
            }
        ]

    def test_email_service_initialization(self, email_service):
        """测试邮件服务初始化"""
        assert email_service.host == TEST_SMTP_CONFIG["host"]
        assert email_service.port == TEST_SMTP_CONFIG["port"]
        assert email_service.username == TEST_SMTP_CONFIG["username"]

    def test_render_html_template(self, email_service, sample_quotes):
        """测试HTML模板渲染"""
        date_str = "2026年01月17日"

        html = email_service._render_html_template(sample_quotes, date_str)

        # 验证HTML包含关键内容
        assert "今日人生导师智慧" in html
        assert date_str in html
        assert "钟南山" in html
        assert "健康" in html
        assert "健康是1" in html

    def test_render_html_quote_distribution(self, email_service, sample_quotes):
        """测试HTML模板中的主题分布统计"""
        html = email_service._render_html_template(sample_quotes, "2026-01-17")

        # 验证包含主题分布部分
        assert "本日主题分布" in html or "主题" in html

    def test_prepare_email_content(self, email_service, sample_quotes):
        """测试邮件内容准备"""
        subject, html, text = email_service._prepare_email_content(
            quotes=sample_quotes,
            date_str="2026年01月17日 星期五"
        )

        # 验证主题
        assert "今日人生导师智慧" in subject
        assert "2026年01月17日" in subject

        # 验证HTML内容
        assert html
        assert isinstance(html, str)
        assert len(html) > 0

        # 验证纯文本内容
        assert text
        assert isinstance(text, str)

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service, sample_quotes):
        """测试成功发送邮件（使用mock）"""
        with patch.object(email_service, '_send_smtp', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await email_service.send_email(
                to_email="recipient@example.com",
                quotes=sample_quotes,
                date_str="2026年01月17日"
            )

            assert result is True
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, email_service, sample_quotes):
        """测试发送邮件失败"""
        with patch.object(email_service, '_send_smtp', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = False

            result = await email_service.send_email(
                to_email="recipient@example.com",
                quotes=sample_quotes,
                date_str="2026年01月17日"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_send_email_with_exception(self, email_service, sample_quotes):
        """测试发送邮件时发生异常"""
        with patch.object(email_service, '_send_smtp', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("SMTP connection error")

            result = await email_service.send_email(
                to_email="recipient@example.com",
                quotes=sample_quotes,
                date_str="2026年01月17日"
            )

            assert result is False

    def test_escape_html(self, email_service):
        """测试HTML转义功能"""
        # 测试特殊字符转义
        dangerous_content = "<script>alert('test')</script>"
        escaped = email_service._escape_html(dangerous_content)

        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped

    def test_format_quote_html(self, email_service):
        """测试单条语录HTML格式化"""
        quote = {
            "keyword": "健康",
            "mentor_name": "钟南山",
            "content": "测试内容<br><script>alert('xss')</script>"
        }

        html = email_service._format_quote_html(quote)

        # 验证关键词和导师名被转义
        assert "【健康】" in html or "健康" in html
        assert "钟南山" in html

        # 验证危险内容被转义
        assert "<script>" not in html
        assert "<br>" not in html or "&lt;br&gt;" in html


class TestEmailTemplates:
    """邮件模板测试"""

    def test_template_exists(self):
        """测试模板文件是否存在"""
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "daily_quote.html"
        assert template_path.exists(), f"Template file not found: {template_path}"

    def test_template_structure(self):
        """测试模板文件结构"""
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "daily_quote.html"

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证包含必要元素
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "</html>" in content
        assert "{{date_str}}" in content or "{date_str}" in content
        assert "{{quotes_html}}" in content or "{quotes_html}" in content

    def test_template_responsive_design(self):
        """测试模板响应式设计"""
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "templates" / "daily_quote.html"

        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 验证包含viewport设置
        assert "viewport" in content

        # 验证包含响应式CSS
        assert "@media" in content or "max-width" in content


@pytest.mark.integration
class TestRealEmailSending:
    """
    集成测试：真实邮件发送
    注意：这些测试会发送真实邮件
    运行时需要: pytest -m integration -v
    """

    @pytest.mark.skipif(
        not os.getenv("SMTP_HOST") or not os.getenv("TEST_EMAIL"),
        reason="SMTP credentials not set"
    )
    @pytest.mark.asyncio
    async def test_real_email_sending(self):
        """真实邮件发送测试"""
        import os

        smtp_config = {
            "host": os.getenv("SMTP_HOST"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("FROM_EMAIL", "test@example.com"),
            "from_name": "PersonalTeachers Test"
        }

        service = EmailService(**smtp_config)

        sample_quotes = [
            {
                "id": 1,
                "keyword": "测试",
                "mentor_name": "测试导师",
                "mentor_category": "test",
                "content": "这是一封测试邮件，用于验证邮件发送功能。",
                "created_at": datetime.now().isoformat()
            }
        ]

        result = await service.send_email(
            to_email=os.getenv("TEST_EMAIL"),
            quotes=sample_quotes,
            date_str="测试日期"
        )

        assert result is True

    @pytest.mark.skipif(
        not os.getenv("SMTP_HOST"),
        reason="SMTP_HOST not set"
    )
    @pytest.mark.asyncio
    async def test_email_delivery_time(self):
        """测试邮件发送耗时"""
        import os
        import time

        smtp_config = {
            "host": os.getenv("SMTP_HOST"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": "test@example.com",
            "from_name": "Test"
        }

        service = EmailService(**smtp_config)

        # Mock实际发送，只测试连接建立时间
        with patch.object(service, '_send_smtp', new_callable=AsyncMock) as mock_send:
            async def mock_send_with_delay(*args, **kwargs):
                time.sleep(0.1)  # 模拟网络延迟
                return True

            mock_send.side_effect = mock_send_with_delay

            start_time = time.time()
            await service.send_email(
                to_email="test@example.com",
                quotes=[],
                date_str="Test"
            )
            elapsed = time.time() - start_time

            # 邮件发送应在5秒内完成
            assert elapsed < 5.0, f"Email sending took {elapsed:.2f}s, expected < 5s"
