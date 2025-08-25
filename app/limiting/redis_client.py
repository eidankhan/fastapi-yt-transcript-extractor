import redis.asyncio as redis
import os
from .config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
