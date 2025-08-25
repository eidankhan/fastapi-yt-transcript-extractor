import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Postgres
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Tier test keys
RL_TEST_KEYS = os.getenv("RL_TEST_KEYS", "free-key-1:free,pro-key-1:pro,ent-key-1:enterprise")



def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default

TIER_LIMITS: Dict[str, Dict[str, int]] = {
    # daily quotas by default; tune via env
    "free": {
        "limit": _env_int("RL_FREE_LIMIT", 100),
        "period": _env_int("RL_FREE_PERIOD", 86400),  # 24h
    },
    "pro": {
        "limit": _env_int("RL_PRO_LIMIT", 5000),
        "period": _env_int("RL_PRO_PERIOD", 86400),
    },
    "enterprise": {
        "limit": _env_int("RL_ENT_LIMIT", 50000),
        "period": _env_int("RL_ENT_PERIOD", 86400),
    },
}

DEFAULT_TIER = os.getenv("RL_DEFAULT_TIER", "free")
VALID_TIERS = set(TIER_LIMITS.keys())

# Optional: quick test mapping via env (comma-separated key:tier pairs)
# Example: RL_TEST_KEYS="abc123:pro,xyz789:enterprise"
def _parse_test_keys(env_val: str | None):
    mapping = {}
    if not env_val:
        return mapping
    for pair in env_val.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            continue
        k, v = pair.split(":", 1)
        k, v = k.strip(), v.strip()
        if k and v in VALID_TIERS:
            mapping[k] = v
    return mapping

TEST_KEY_TIER_MAP = _parse_test_keys(os.getenv("RL_TEST_KEYS"))
