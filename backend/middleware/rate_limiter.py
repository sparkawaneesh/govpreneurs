import os
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

# Use Redis as storage if REDIS_URL is provided, otherwise default to in-memory
storage_uri = os.getenv("REDIS_URL", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    strategy="fixed-window"
)

def log_rate_limit_exceeded(request, exc):
    """
    Structured logging for when rate limits are triggered.
    """
    logger.warning(
        f"Rate limit exceeded: client={request.client.host}, "
        f"url={request.url.path}, "
        f"limit={exc.detail}"
    )
