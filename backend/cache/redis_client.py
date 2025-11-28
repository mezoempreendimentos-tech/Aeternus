# Cliente Redis

import redis.asyncio as redis
from backend.config.server_config import REDIS_URL

class RedisClient:
    def __init__(self):
        self.redis = None
    
    async def connect(self):
        self.redis = await redis.from_url(REDIS_URL)
    
    async def disconnect(self):
        await self.redis.close()
    
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        await self.redis.delete(key)
    
    async def publish(self, channel: str, message: str):
        await self.redis.publish(channel, message)
