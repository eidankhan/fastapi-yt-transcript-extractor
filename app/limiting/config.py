import os
from typing import Dict

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
