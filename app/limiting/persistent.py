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
