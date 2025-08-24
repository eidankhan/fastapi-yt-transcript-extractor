from fastapi import Request, HTTPException
import time
from .memory import InMemoryLimiter
from .persistent import RedisLimiter, TokenBucketLimiter

# Configure limiters
limiter = InMemoryLimiter(max_per_window=3, window_seconds=60)
redis_limiter = RedisLimiter(limit=3, period_seconds=86400)

# Example: 100 requests per day
token_bucket = TokenBucketLimiter(limit=3, period_seconds=86400)

# In-memory rate limiter dependency
def rate_limit_dependency():
    async def _dep(request: Request):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        allowed, limit, remaining, reset_ts = await limiter.check(api_key)
        reset_in = max(0, reset_ts - int(time.time()))

        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_ts),
        }

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {reset_in} seconds."
            )

    return _dep  # ← Important: return the inner async function


# Redis-based persistent rate limiter dependency
def redis_rate_limit_dependency():
    async def _dep(request: Request):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        allowed, limit, remaining, reset_ts = await redis_limiter.check(api_key)
        reset_in = max(0, reset_ts - int(time.time()))

        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_ts),
        }

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {reset_in} seconds."
            )

    return _dep  # ← Must return the async function

def token_bucket_dependency():
    async def _dep(request: Request):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        allowed, limit, remaining, reset_ts = await token_bucket.check(api_key)
        reset_in = max(0, reset_ts - int(time.time()))

        # Attach headers for reporting
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_ts),
        }

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"No tokens left. Bucket refills in {reset_in} seconds."
            )

    return _dep