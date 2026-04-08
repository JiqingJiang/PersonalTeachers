"""Phase 3 测试：邮件发送池、调度器、管理后台"""

import pytest
from unittest.mock import AsyncMock, patch

from app.services.email_sender import EmailSenderPool


class TestEmailSenderPool:
    """邮箱轮询池测试"""

    def test_round_robin_selection(self):
        """测试轮询选择"""
        senders = [
            {"email": "a@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 0,
             "last_sent_date": "2026-04-07"},
            {"email": "b@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 0,
             "last_sent_date": "2026-04-07"},
        ]
        pool = EmailSenderPool(senders)

        s1 = pool.get_next_sender()
        s2 = pool.get_next_sender()
        assert s1 is not None
        assert s2 is not None
        assert s1["email"] != s2["email"]  # 轮询到不同邮箱

    def test_skips_exhausted_sender(self):
        """测试跳过已耗尽的邮箱"""
        senders = [
            {"email": "a@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 200,
             "last_sent_date": "2026-04-07"},
            {"email": "b@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 50,
             "last_sent_date": "2026-04-07"},
        ]
        pool = EmailSenderPool(senders)
        sender = pool.get_next_sender()
        assert sender is not None
        assert sender["email"] == "b@test.com"

    def test_all_exhausted_returns_none(self):
        """测试所有邮箱耗尽时返回 None"""
        senders = [
            {"email": "a@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 200,
             "last_sent_date": "2026-04-07"},
        ]
        pool = EmailSenderPool(senders)
        assert pool.get_next_sender() is None

    def test_resets_daily_counter(self):
        """测试每日计数器重置"""
        senders = [
            {"email": "a@test.com", "smtp_host": "smtp.test.com", "smtp_port": 587,
             "smtp_password": "pass", "daily_limit": 200, "sent_today": 200,
             "last_sent_date": "2026-04-06"},  # 昨天的日期
        ]
        pool = EmailSenderPool(senders)
        sender = pool.get_next_sender()
        assert sender is not None  # 新的一天，计数器重置
        assert sender["sent_today"] == 0


class TestAdminAPI:
    """管理后台 API 测试"""

    @pytest.mark.asyncio
    async def test_admin_required(self, client, db_session):
        """测试非管理员被拒绝"""
        from app.models import User
        from app.utils.security import hash_password

        user = User(
            email="normal@test.com",
            password_hash=hash_password("test123"),
            is_admin=False,
        )
        db_session.add(user)
        await db_session.commit()

        # 登录
        resp = await client.post("/api/v1/auth/login", json={
            "email": "normal@test.com", "password": "test123",
        })
        token = resp.json()["access_token"]

        # 访问管理后台
        resp = await client.get("/api/v1/admin/users/", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_list_users(self, client, db_session):
        """测试管理员列出用户"""
        from app.models import User
        from app.utils.security import hash_password

        admin = User(
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            is_admin=True,
        )
        db_session.add(admin)
        await db_session.commit()

        # 登录
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "admin123",
        })
        token = resp.json()["access_token"]

        # 列出用户
        resp = await client.get("/api/v1/admin/users/", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_ai_models_crud(self, client, db_session):
        """测试 AI 模型 CRUD"""
        from app.models import User, AIModel
        from app.utils.security import hash_password

        admin = User(
            email="admin2@test.com",
            password_hash=hash_password("admin123"),
            is_admin=True,
        )
        db_session.add(admin)
        await db_session.commit()

        # 登录
        resp = await client.post("/api/v1/auth/login", json={
            "email": "admin2@test.com", "password": "admin123",
        })
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 创建 AI 模型
        resp = await client.post("/api/v1/admin/ai-models/", json={
            "name": "TestModel",
            "provider": "custom",
            "base_url": "https://api.test.com",
            "api_key": "sk-test-key-12345678",
            "model_id": "test-v1",
            "priority": 1,
        }, headers=headers)
        assert resp.status_code == 201

        # 列出 AI 模型
        resp = await client.get("/api/v1/admin/ai-models/", headers=headers)
        assert resp.status_code == 200
        models = resp.json()
        assert any(m["name"] == "TestModel" for m in models)

        # 获取模型 ID
        model_id = next(m["id"] for m in models if m["name"] == "TestModel")

        # 更新
        resp = await client.put(f"/api/v1/admin/ai-models/{model_id}", json={
            "is_active": True,
        }, headers=headers)
        assert resp.status_code == 200

        # 删除
        resp = await client.delete(f"/api/v1/admin/ai-models/{model_id}", headers=headers)
        assert resp.status_code == 200
