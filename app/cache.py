"""
Caching Module for YouTube Niche Discovery Engine

This module provides smart caching functionality with TTL support
to reduce API costs and improve performance.
"""

import json
import time
import hashlib
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APICache:
    """Smart caching layer with TTL support to reduce API costs"""
    
    def __init__(self, ttl_seconds=3600):  # 1 hour default
        self.cache = {}
        self.ttl = ttl_seconds
        self.hit_count = 0
        self.miss_count = 0
        logger.info(f"APICache initialized with TTL: {ttl_seconds}s")
    
    def _generate_key(self, prefix: str, params: dict) -> str:
        """Generate a cache key from prefix and parameters"""
        key_string = f"{prefix}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached value if valid"""
        if key in self.cache:
            entry = self.cache[key]
            if self.is_valid(key):
                self.hit_count += 1
                logger.debug(f"Cache HIT: {key}")
                return entry['value']
            else:
                # Expired, remove it
                del self.cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        
        self.miss_count += 1
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: dict) -> None:
        """Cache a value with timestamp"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
        logger.debug(f"Cache SET: {key}")
    
    def is_valid(self, key: str) -> bool:
        """Check if cached entry is still valid"""
        if key not in self.cache:
            return False
        entry = self.cache[key]
        return (time.time() - entry['timestamp']) < self.ttl
    
    def get_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        return {
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': round(hit_rate, 1),
            'total_entries': len(self.cache)
        }
    
    def clear_expired(self) -> int:
        """Remove expired entries and return count of removed items"""
        expired_keys = [k for k in self.cache.keys() if not self.is_valid(k)]
        for key in expired_keys:
            del self.cache[key]
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        return len(expired_keys)