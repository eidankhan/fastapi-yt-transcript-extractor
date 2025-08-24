from fastapi import Request, HTTPException, Depends
from .memory import InMemoryLimiter
import time

# Configure limiter: 3 requests per 60 seconds
limiter = InMemoryLimiter(max_per_window=3, window_seconds=60)

def rate_limit_dependency():
    async def _dep(request: Request):
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        allowed, limit, remaining, reset_ts = await limiter.check(api_key)
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
                detail=f"Rate limit exceeded. Try again in {reset_in} seconds."
            )

    return _dep
