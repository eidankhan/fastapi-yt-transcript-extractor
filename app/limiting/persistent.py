import time
from typing import Tuple
from .redis_client import r

class RedisLimiter:
    """
    Persistent rate limiter using Redis.
    Supports daily/monthly counters with per-user keys.
    """

    def __init__(self, limit: int = 3, period_seconds: int = 86400):
        self.limit = limit
        self.period = period_seconds  # default 1 day

    def _key(self, api_key: str) -> str:
        return f"user:{api_key}:count"

    async def check(self, api_key: str) -> Tuple[bool, int, int, int]:
        """
        Returns: allowed, limit, remaining, reset_ts
        """
        key = self._key(api_key)
        now = int(time.time())

        # Increment the counter atomically
        current = await r.incr(key)

        # If key is new, set expiration
        ttl = await r.ttl(key)
        if ttl == -1:  # key exists but no TTL
            await r.expire(key, self.period)
        elif ttl == -2:  # key does not exist (race condition)
            await r.expire(key, self.period)

        remaining = max(0, self.limit - current)
        reset_ts = now + (ttl if ttl > 0 else self.period)

        allowed = current <= self.limit
        return allowed, self.limit, remaining, reset_ts
    
class TokenBucketLimiter:
    def __init__(self, limit: int, period_seconds: int, redis_url: str = "redis://redis:6379/0"):
        """
        Token Bucket Limiter
        :param limit: Max tokens per period (e.g., 100/day).
        :param period_seconds: Reset interval (e.g., 86400 = 24h).
        """
        self.limit = limit
        self.period_seconds = period_seconds
        self.redis_url = redis_url
        self.redis = None

    async def init(self):
        if self.redis is None:
            self.redis = await r.from_url(self.redis_url, decode_responses=True)

    async def check(self, api_key: str) -> Tuple[bool, int, int, int]:
        """
        Check if the user has tokens available.
        Returns (allowed, limit, remaining, reset_ts).
        """
        await self.init()

        now = int(time.time())
        period_start = now - (now % self.period_seconds)
        reset_ts = period_start + self.period_seconds

        bucket_key = f"bucket:{api_key}:{period_start}"

        # Initialize tokens if not present
        tokens = await self.redis.get(bucket_key)
        if tokens is None:
            tokens = self.limit
            await self.redis.set(bucket_key, tokens, ex=self.period_seconds)
        else:
            tokens = int(tokens)

        if tokens > 0:
            await self.redis.decr(bucket_key)
            tokens -= 1
            return True, self.limit, tokens, reset_ts

        return False, self.limit, 0, reset_ts