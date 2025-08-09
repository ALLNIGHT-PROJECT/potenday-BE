"""
Redis connection and operations
"""
import redis.asyncio as redis
from typing import Optional
import json
import os

# Redis client instance
redis_client: Optional[redis.Redis] = None

async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    
    if redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
    
    return redis_client

async def set_token(key: str, value: dict, expiry: int = 3600):
    """
    Store token in Redis with expiry
    
    Args:
        key: Token key (e.g., "refresh_token:{token}")
        value: Token data dictionary
        expiry: Expiration time in seconds
    """
    client = await get_redis()
    await client.setex(key, expiry, json.dumps(value))

async def get_token(key: str) -> Optional[dict]:
    """
    Get token from Redis
    
    Args:
        key: Token key
        
    Returns:
        Token data or None if not found
    """
    client = await get_redis()
    data = await client.get(key)
    if data:
        return json.loads(data)
    return None

async def delete_token(key: str) -> bool:
    """
    Delete token from Redis
    
    Args:
        key: Token key
        
    Returns:
        True if deleted, False otherwise
    """
    client = await get_redis()
    result = await client.delete(key)
    return result > 0

async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None