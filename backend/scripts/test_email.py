#!/usr/bin/env python3
"""
测试邮件发送功能
验证QQ邮箱SMTP配置是否正确
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.email_service import EmailService
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv(PROJECT_ROOT / ".env")


async def test_email():
    """测试邮件发送"""
    print("📧 测试QQ邮箱SMTP配置")
    print("=" * 50)

    # 检查配置
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("EMAIL_FROM", smtp_username)

    print(f"SMTP服务器: {smtp_host}:{smtp_port}")
    print(f"发件邮箱: {from_email}")
    print(f"收件邮箱: {smtp_username}")
    print("")

    # 创建邮件服务
    email_service = EmailService(
        host=smtp_host,
        port=smtp_port,
        username=smtp_username,
        password=smtp_password,
        from_email=from_email,
        from_name="PersonalTeachers"
    )

    # 准备测试语录
    test_quotes = [
        {
            "id": 1,
            "keyword": "测试",
            "mentor_name": "测试导师",
            "mentor_category": "test",
            "content": "这是一封测试邮件，用于验证QQ邮箱SMTP配置是否正确。<br><br>如果你收到这封邮件，说明配置成功！🎉",
            "created_at": "2026-01-17T18:00:00"
        }
    ]

    try:
        print("正在生成邮件HTML...")
        html_content = email_service.render_daily_quote_email(test_quotes)

        print("正在发送测试邮件...")
        result = await email_service.send_email(
            to_email=smtp_username,
            subject="📚 PersonalTeachers 邮件发送测试",
            html_content=html_content
        )

        if result:
            print("")
            print("✅ 邮件发送成功！")
            print(f"📬 请检查邮箱: {smtp_username}")
            print(f"   如果没收到，请查看垃圾邮件箱")
            print("")
            print("📋 QQ邮箱配置总结:")
            print("  • SMTP服务器: smtp.qq.com")
            print("  • 端口: 587 (TLS)")
            print("  • 密码: 授权码（非QQ密码）")
        else:
            print("")
            print("❌ 邮件发送失败")
            print("\n常见问题:")
            print("1. 授权码是否正确？（不是QQ密码）")
            print("2. SMTP服务是否已开启？")
            print("3. 网络连接是否正常？")

    except Exception as e:
        print("")
        print(f"❌ 发送出错: {e}")
        print("\n请检查:")
        print("1. .env 文件中的 SMTP_PASSWORD 是否是授权码")
        print("2. QQ邮箱是否开启了SMTP服务")
        print("3. 端口587是否被防火墙阻止")


if __name__ == "__main__":
    asyncio.run(test_email())
