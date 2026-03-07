import os
import json
import redis
import logging
from typing import Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CacheService:
    """
    Unified caching service using Redis.
    """
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.from_url(self.redis_url)
            self.client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the cache.
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                logger.info(f"Cache HIT: key={key}")
                return json.loads(value)
            logger.info(f"Cache MISS: key={key}")
            return None
        except Exception as e:
            logger.error(f"Error reading from cache: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: int = 900):
        """
        Sets a value in the cache with a TTL (default 15 minutes).
        """
        if not self.client:
            return
        
        try:
            serialized_value = json.dumps(value)
            self.client.setex(key, ttl, serialized_value)
            logger.info(f"Cache SET: key={key}, ttl={ttl}")
        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")

    def delete(self, key: str):
        """
        Deletes a key from the cache.
        """
        if not self.client:
            return
        
        try:
            self.client.delete(key)
            logger.info(f"Cache DELETE: key={key}")
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
