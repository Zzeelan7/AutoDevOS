import redis.asyncio as redis
import json
import os
from typing import Any, List, Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


class RedisClient:
    def __init__(self):
        self.connection_pool = None
        self.client = None

    async def connect(self):
        """Initialize async Redis connection"""
        self.connection_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
        self.client = redis.Redis(connection_pool=self.connection_pool)
        # Test connection
        await self.client.ping()
        print("✓ Redis connected")

    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()

    async def publish_event(self, job_id: str, event: Dict[str, Any]):
        """Publish event to job channel"""
        channel = f"job:{job_id}"
        await self.client.publish(channel, json.dumps(event))

    async def push_job(self, job_id: str):
        """Push job to queue"""
        await self.client.rpush("job_queue", job_id)

    async def pop_job(self) -> str | None:
        """Pop next job from queue (blocking)"""
        result = await self.client.blpop("job_queue", timeout=1)
        if result:
            return result[1]  # result is (key, value)
        return None

    async def set_cache(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value with TTL"""
        await self.client.setex(key, ttl, json.dumps(value))

    async def get_cache(self, key: str) -> Any | None:
        """Get cached value"""
        result = await self.client.get(key)
        if result:
            return json.loads(result)
        return None

    async def delete_cache(self, key: str):
        """Delete cached value"""
        await self.client.delete(key)

    async def subscribe(self, channel: str):
        """Subscribe to channel (returns async iterator)"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub


# Global instance
redis_client = RedisClient()
