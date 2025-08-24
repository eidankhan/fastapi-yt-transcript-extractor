from .redis_client import r
from .config import DEFAULT_TIER, VALID_TIERS, TEST_KEY_TIER_MAP

def _tier_key(api_key: str) -> str:
    return f"user:{api_key}:tier"

async def get_tier(api_key: str) -> str:
    """
    Returns the tier for a given api_key.
    Order of precedence:
      1) Redis key user:{api_key}:tier
      2) TEST_KEY_TIER_MAP (from env RL_TEST_KEYS) for quick manual testing
      3) DEFAULT_TIER
    """
    tier = await r.get(_tier_key(api_key))
    if tier in VALID_TIERS:
        return tier

    # fallback for local/dev without DB
    tier = TEST_KEY_TIER_MAP.get(api_key)
    if tier in VALID_TIERS:
        return tier

    return DEFAULT_TIER

async def set_tier(api_key: str, tier: str) -> None:
    """
    Manually set a user's tier in Redis (e.g., via admin task or script).
    """
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier '{tier}'. Valid: {sorted(VALID_TIERS)}")
    await r.set(_tier_key(api_key), tier)
