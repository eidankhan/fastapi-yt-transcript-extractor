import time
import asyncio
from typing import Dict, Tuple

class InMemoryLimiter:
    def __init__(self, max_per_window: int = 3, window_seconds: int = 60):
        self.max = max_per_window
        self.window = window_seconds
        self._store: Dict[str, Tuple[int, int]] = {}  # api_key -> (count, window_start)
        self._lock = asyncio.Lock()

    def _key(self, api_key: str) -> str:
        return f"user:{api_key}"

    async def check(self, api_key: str) -> Tuple[bool, int, int, int]:
        now = int(time.time())
        key = self._key(api_key)

        async with self._lock:
            count, window_start = self._store.get(key, (0, now))

            # Reset window if expired
            if now - window_start >= self.window:
                count = 0
                window_start = now

            count += 1
            self._store[key] = (count, window_start)

            allowed = count <= self.max
            remaining = max(0, self.max - count)
            reset_ts = window_start + self.window
            return allowed, self.max, remaining, reset_ts
