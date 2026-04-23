"""认证 API 测试"""

import pytest
from sqlalchemy import select

from app.models import User
from app.utils.security import hash_password, verify_password


@pytest.mark.asyncio
async def test_register_and_login(client, db_session):
    """测试注册 → 登录流程"""
    # 注意：由于验证码需要 SMTP，测试中我们直接在数据库中操作
    # 先创建一个用户来测试登录
    from app.models import User
    user = User(
        email="test@example.com",
        password_hash=hash_password("test123456"),
        nickname="测试用户",
    )
    db_session.add(user)
    await db_session.commit()

    # 测试登录
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "test123456",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, db_session):
    """测试错误密码登录"""
    user = User(
        email="wrong@example.com",
        password_hash=hash_password("correct123"),
    )
    db_session.add(user)
    await db_session.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrong123",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, db_session):
    """测试获取当前用户信息"""
    user = User(
        email="me@example.com",
        password_hash=hash_password("test123456"),
        nickname="我",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 登录获取 token
    resp = await client.post("/api/v1/auth/login", json={
        "email": "me@example.com",
        "password": "test123456",
    })
    token = resp.json()["access_token"]

    # 获取用户信息
    resp = await client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_refresh_token(client, db_session):
    """测试刷新 token"""
    user = User(
        email="refresh@example.com",
        password_hash=hash_password("test123456"),
    )
    db_session.add(user)
    await db_session.commit()

    resp = await client.post("/api/v1/auth/login", json={
        "email": "refresh@example.com",
        "password": "test123456",
    })
    refresh_token = resp.json()["refresh_token"]

    resp = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_password_hashing():
    """测试密码哈希"""
    password = "my-secure-password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_update_profile(client, db_session):
    """测试更新用户信息"""
    user = User(
        email="profile@example.com",
        password_hash=hash_password("test123456"),
    )
    db_session.add(user)
    await db_session.commit()

    # 登录
    resp = await client.post("/api/v1/auth/login", json={
        "email": "profile@example.com",
        "password": "test123456",
    })
    token = resp.json()["access_token"]

    # 更新 profile
    resp = await client.put("/api/v1/users/profile", json={
        "nickname": "新昵称",
        "age": 24,
        "profession": "学生",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["nickname"] == "新昵称"
    assert data["age"] == 24
