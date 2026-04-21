import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

BASE_URL = "/api/v1"
AUTH_URL = f"{BASE_URL}/auth"

async def test_register_success(client: AsyncClient):
    response = await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "reader"
    assert data["username"] == "testuser"
    assert "hashed_password" not in data

async def test_register_duplicate_email(client: AsyncClient):
    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    response = await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    assert response.status_code == 409

async def test_register_weak_password(client: AsyncClient):
    response = await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "passwor"
    })

    assert response.status_code == 422

async def test_register_invalid_email(client: AsyncClient):
    response = await client.post(f"{AUTH_URL}/register", json={
        "email": "testexample.com",
        "username": "testuser",
        "password": "password"
    })

    assert response.status_code == 422

async def test_login_success(client: AsyncClient):
    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    response = await client.post(f"{AUTH_URL}/login", json={
        "email": "test@example.com",
        "password": "password"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies

async def test_login_wrong_password(client: AsyncClient):
    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    response = await client.post(f"{AUTH_URL}/login", json={
        "email": "test@example.com",
        "password": "password22"
    })

    assert response.status_code == 401

async def test_login_wrong_email(client: AsyncClient):
    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })

    response = await client.post(f"{AUTH_URL}/login", json={
        "email": "test2@example.com",
        "password": "password"
    })

    assert response.status_code == 401

async def test_login_inactive_user(client: AsyncClient, db: AsyncSession):
    response_user = await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password"
    })
    assert response_user.status_code == 201

    response_admin = await client.post(f"{AUTH_URL}/register", json={
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "password"
    })
    assert response_admin.status_code == 201

    from sqlalchemy import update
    from app.models.db import UserDB
    await db.execute(update(UserDB).where(UserDB.email == "admin@example.com").values(role="admin"))
    await db.commit()

    admin_login = await client.post(f"{AUTH_URL}/login", json={
        "email": "admin@example.com",
        "password": "password"
    })

    assert admin_login.status_code == 200

    admin = admin_login.json()

    user = response_user.json()

    patch_response = await client.patch(f"{BASE_URL}/users/{user['id']}", headers={"Authorization": f"Bearer {admin['access_token']}"})

    assert patch_response.status_code == 200

    response = await client.post(f"{AUTH_URL}/login", json={
        "email": user["email"],
        "password": "password"
    })

    assert response.status_code == 401
