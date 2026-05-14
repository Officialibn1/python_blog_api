import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.app import app
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.cache import connect_redis, disconnect_redis

test_engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(autouse=True)
def disable_rate_limit():
    from app.core.limiter import limiter
    original_enabled = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = original_enabled

@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def setup_database():
    await connect_redis()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await disconnect_redis()

@pytest_asyncio.fixture(autouse=True)
async def reset_db():
    yield
    async with test_engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE TABLE users, posts, comments, categories, tags, post_tags RESTART IDENTITY CASCADE"
        ))

@pytest_asyncio.fixture
async def db():
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_client(client: AsyncClient, db: AsyncSession):
    from sqlalchemy import update
    from app.models.db import UserDB

    await client.post("/api/v1/auth/register", json={
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "password"
    })

    await db.execute(update(UserDB).where(UserDB.email == "admin@example.com").values(role="admin"))
    await db.commit()

    login = await client.post("/api/v1/auth/login", json={
        "email": "admin@example.com",
        "password": "password"
    })

    token = login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
