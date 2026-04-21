import pytest
from httpx import AsyncClient
from app.lib.constants import POST_URL, CATEGORY_URL, TAG_URL, AUTH_URL

async def test_create_post_unauthenticated(client: AsyncClient):
    response = await client.post(f"{POST_URL}/", json={
      "title": "string",
      "content": "string",
      "category_id": 0,
      "tag_ids": [],
      "published": False
    })

    assert response.status_code == 401

async def test_create_post_success(admin_client: AsyncClient):
    await admin_client.post(f"{CATEGORY_URL}/", json={
      "name": "category-1"
    })

    await admin_client.post(f"{TAG_URL}/", json={
      "name": "tag-1"
    })

    response = await admin_client.post(f"{POST_URL}/", json={
      "title": "Test post",
      "content": "Test post",
      "category_id": 1,
      "tag_ids": [1],
      "published": False
    })
    assert response.status_code == 201


async def test_get_all_posts_success(client: AsyncClient):
    response = await client.get(f"{POST_URL}/")
    assert response.status_code == 200

async def test_get_post_success(admin_client: AsyncClient):
    await admin_client.post(f"{CATEGORY_URL}/", json={
      "name": "category-1"
    })

    await admin_client.post(f"{TAG_URL}/", json={
      "name": "tag-1"
    })

    await admin_client.post(f"{POST_URL}/", json={
      "title": "Test post",
      "content": "Test post",
      "category_id": 1,
      "tag_ids": [1],
      "published": False
    })

    response = await admin_client.get(f"{POST_URL}/{1}")
    assert response.status_code == 200

async def test_get_post_not_found(client: AsyncClient):
    response = await client.get(f"{POST_URL}/{22}")
    assert response.status_code == 404

async def test_update_post_wrong_user(admin_client: AsyncClient, client: AsyncClient):
    await admin_client.post(f"{CATEGORY_URL}/", json={
      "name": "category-1"
    })

    await admin_client.post(f"{TAG_URL}/", json={
      "name": "tag-1"
    })

    await admin_client.post(f"{POST_URL}/", json={
      "title": "Test post",
      "content": "Test post",
      "category_id": 1,
      "tag_ids": [1],
      "published": False
    })

    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "username",
        "password": "password"
    })

    user_login = await client.post(f"{AUTH_URL}/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = user_login.json()["access_token"]
    response = await client.patch(
        f"{POST_URL}/1",
        headers={"Authorization": f"Bearer {token}"}, json={
            "title": "Test edit",
            "content": "Test edit",
            "category_id": 1,
            "tag_ids": [1],
            "published": False
        }
    )
    assert response.status_code == 403

async def test_delete_post_as_admin(admin_client: AsyncClient, client: AsyncClient):
    await client.post(f"{AUTH_URL}/register", json={
        "email": "test@example.com",
        "username": "username",
        "password": "password"
    })

    user_login = await client.post(f"{AUTH_URL}/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    token = user_login.json()["access_token"]

    await admin_client.post(f"{CATEGORY_URL}/", json={
      "name": "category-1"
    })

    await admin_client.post(f"{TAG_URL}/", json={
      "name": "tag-1"
    })

    await client.post(
        f"{POST_URL}/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test post",
            "content": "Test post",
            "category_id": 1,
            "tag_ids": [1],
            "published": False
        }
    )

    response = await admin_client.delete(f"{POST_URL}/1")
    assert response.status_code == 204
