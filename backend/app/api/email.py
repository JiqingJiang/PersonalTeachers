"""
邮件相关API端点

提供测试邮件发送、查看日志等功能
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
from loguru import logger

from app.services.email_service import get_email_service
from app.core import get_quote_engine


router = APIRouter(prefix="/api/email", tags=["邮件"])


@router.post("/test")
async def send_test_email():
    """
    发送测试邮件

    生成3条测试语录并发送到用户邮箱
    """
    try:
        logger.info("开始生成测试语录...")
        # 生成测试语录
        engine = get_quote_engine()
        quotes_data = await engine.generate_quotes(count=3)

        if not quotes_data:
            logger.error("语录生成失败 - 返回为空")
            raise HTTPException(status_code=500, detail="Failed to generate test quotes")

        logger.info(f"语录生成成功: {len(quotes_data)} 条")

        # 发送邮件
        email_service = get_email_service()
        html_content = email_service.render_daily_quote_email(
            quotes=quotes_data,
            date=datetime.now()
        )

        logger.info(f"HTML渲染完成，长度: {len(html_content)}")

        # 获取用户邮箱
        config = _load_config()
        user_email = config.get('user', {}).get('email')

        if not user_email:
            logger.error("用户邮箱未配置")
            raise HTTPException(status_code=400, detail="User email not configured")

        logger.info(f"开始发送邮件到: {user_email}")

        success = await email_service.send_email(
            to_email=user_email,
            subject="🧪 PersonalTeachers 测试邮件",
            html_content=html_content
        )

        if success:
            logger.info(f"测试邮件发送成功: {user_email}")
            return {
                "message": "测试邮件发送成功",
                "to_email": user_email,
                "quote_count": len(quotes_data)
            }
        else:
            logger.error(f"邮件发送返回False: {user_email}")
            raise HTTPException(status_code=500, detail="Failed to send test email")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/logs")
async def get_email_logs(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30, description="最近N天的日志")
):
    """
    获取邮件发送日志

    显示最近N天的邮件发送记录
    """
    try:
        from app.models.database import EmailLogDB
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from pathlib import Path

        db_path = Path(__file__).parent.parent.parent.parent / "storage" / "quotes.db"
        engine = create_engine(f"sqlite:///{db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            logs = session.query(EmailLogDB).filter(
                EmailLogDB.sent_at >= cutoff_date
            ).order_by(EmailLogDB.sent_at.desc()).limit(limit).all()

            return [
                {
                    "id": log.id,
                    "to_email": log.to_email,
                    "subject": log.subject,
                    "sent_at": log.sent_at.isoformat(),
                    "success": bool(log.success),
                    "error_message": log.error_message,
                    "quote_count": log.quote_count
                }
                for log in logs
            ]

        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error fetching email logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _load_config() -> dict:
    """加载配置文件"""
    from pathlib import Path
    import yaml

    config_path = Path(__file__).parent.parent.parent / "data" / "config.yaml"

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
