import time
from typing import Tuple, Dict
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
    
# ... keep your existing RedisLimiter and TokenBucketLimiter here ...

class TieredTokenBucketLimiter:
    """
    Token Bucket with per-tier limits (free/pro/enterprise).
    Uses Redis atomic ops. Keys auto-expire at period end.
    """
    def __init__(self, tier_limits: Dict[str, Dict[str, int]]):
        self.tier_limits = tier_limits

    def _bucket_key(self, api_key: str, tier: str, period_start: int) -> str:
        return f"user:{api_key}:bucket:{tier}:{period_start}"

    async def check(self, api_key: str, tier: str) -> Tuple[bool, int, int, int]:
        cfg = self.tier_limits.get(tier) or self.tier_limits["free"]
        limit = int(cfg["limit"])
        period = int(cfg["period"])

        now = int(time.time())
        period_start = now - (now % period)
        key = self._bucket_key(api_key, tier, period_start)

        # Ensure bucket exists only once per period (nx=True)
        # If it already exists, this is a no-op.
        await r.set(key, limit, ex=period, nx=True)

        # Atomically decrement; if we went below 0, revert and deny
        new_val = await r.decr(key)
        if new_val >= 0:
            remaining = new_val
            ttl = await r.ttl(key)
            reset_ts = now + (ttl if ttl and ttl > 0 else period)
            return True, limit, remaining, reset_ts

        # We overshot (concurrent requests). Undo and reject.
        await r.incr(key)
        ttl = await r.ttl(key)
        reset_ts = now + (ttl if ttl and ttl > 0 else period)
        return False, limit, 0, reset_ts
