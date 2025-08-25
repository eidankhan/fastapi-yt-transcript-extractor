from .redis_client import r
from .config import DEFAULT_TIER, VALID_TIERS, TEST_KEY_TIER_MAP
from app.database import SessionLocal
from app import models

def _tier_key(api_key: str) -> str:
    return f"user:{api_key}:tier"

async def get_tier(api_key: str) -> str:
    """
    Returns the tier for a given api_key.
    Order of precedence:
      1) Database lookup (users table)
      2) Redis key user:{api_key}:tier
      3) TEST_KEY_TIER_MAP (from env RL_TEST_KEYS) for quick manual testing
      4) DEFAULT_TIER
    """

    # 1) Database lookup
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.api_key == api_key).first()
        if user and user.tier in VALID_TIERS:
            return user.tier
    finally:
        db.close()

    # 2) Redis lookup
    tier = await r.get(_tier_key(api_key))
    if tier in VALID_TIERS:
        return tier

    # 3) Testing keys (from config)
    tier = TEST_KEY_TIER_MAP.get(api_key)
    if tier in VALID_TIERS:
        return tier

    # 4) Default fallback
    return DEFAULT_TIER


async def set_tier(api_key: str, tier: str) -> None:
    """
    Manually set a user's tier in Redis (e.g., via admin task or script).
    """
    if tier not in VALID_TIERS:
        raise ValueError(f"Invalid tier '{tier}'. Valid: {sorted(VALID_TIERS)}")
    await r.set(_tier_key(api_key), tier)

def validate_api_key(api_key: str):
    """
    Check if API key exists in the database.
    Raises 401 if not valid.
    """
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == api_key).first()
    db.close()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


def validate_api_key(api_key: str):
    """
    Check if API key exists in the database.
    Raises 401 if not valid.
    """
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.api_key == api_key).first()
    db.close()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user