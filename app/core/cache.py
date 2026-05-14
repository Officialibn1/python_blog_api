from redis.asyncio import Redis, RedisError
from app.core.config import settings

redis: Redis | None = None

async def connect_redis() -> None:
    """
    Create and returns Redis client instance
    """
    global redis
    redis =  Redis.from_url(settings.REDIS_URL)

async def disconnect_redis() -> None:
    """
    """
    global redis
    if redis:
        await redis.aclose()
        redis = None

async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    global redis
    if not redis:
        raise RedisError("Redis instance not initialized")

    await redis.set(key, value, ex=ttl)

async def cache_get(key: str) -> str | None:
    global redis
    if not redis:
        raise RedisError("Redis instance not initialized")

    return await redis.get(key)

async def cache_delete(key: str) -> None:
    global redis
    if not redis:
        raise RedisError("Redis instance not initialized")

    await redis.delete(key)
