import logging
import time
from typing import Any, Dict, Tuple

# -------------------------------
# CACHE CONFIG
# -------------------------------

CACHE_TTL = 300
MAX_CACHE_SIZE = 1000

# -------------------------------
# CACHE STORAGE
# -------------------------------

logger = logging.getLogger(__name__)

# I keep the cache structure simple because this service supports the project
# by making repeated API work cheaper without introducing another dependency.
cache_store: Dict[str, Tuple[float, Any]] = {}

# -------------------------------
# CLEANUP FUNCTION
# -------------------------------

def cleanup_cache() -> None:
    """
    I remove expired or excess entries so the cache helps response times
    without quietly growing into a memory problem for the API.
    """
    current_time = time.time()
    expired_keys = [
        key for key, (ts, _) in cache_store.items()
        if current_time - ts > CACHE_TTL
    ]

    for key in expired_keys:
        del cache_store[key]

    # I drop the oldest records first because recent results are the ones most
    # likely to help the live dashboard or repeated scoring requests.
    if len(cache_store) > MAX_CACHE_SIZE:
        sorted_items = sorted(cache_store.items(), key=lambda item: item[1][0])
        overflow_count = len(cache_store) - MAX_CACHE_SIZE
        for key, _ in sorted_items[:overflow_count]:
            del cache_store[key]

# -------------------------------
# GET FUNCTION
# -------------------------------

def get_from_cache(key: str) -> Any:
    """
    I return a cached value when it is still fresh so repeated project calls
    can stay fast and predictable.
    """
    cleanup_cache()

    if key in cache_store:
        ts, value = cache_store[key]

        if time.time() - ts <= CACHE_TTL:
            logger.info("Cache HIT for key: %s", key)
            return value

        del cache_store[key]

    logger.info("Cache MISS for key: %s", key)
    return None

# -------------------------------
# SET FUNCTION
# -------------------------------

def set_cache(key: str, value: Any) -> None:
    """
    I store values with a timestamp so the cache can support the project’s
    live scoring flow without serving stale results forever.
    """
    cleanup_cache()
    cache_store[key] = (time.time(), value)
