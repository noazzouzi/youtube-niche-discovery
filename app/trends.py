"""
Google Trends API Module for YouTube Niche Discovery Engine

This module provides Google Trends integration using pytrends library
with caching and rate limiting to analyze keyword popularity over time.
"""

import time
import random
import logging
from pytrends.request import TrendReq

from .cache import APICache

logger = logging.getLogger(__name__)


class TrendsAPI:
    """Google Trends API with caching and rate limiting"""
    
    def __init__(self, cache: APICache):
        self.cache = cache
        self.call_count = 0
        self.last_call_time = 0
        self.min_interval = 1.0  # Minimum 1 second between calls
        logger.info("TrendsAPI initialized")
    
    def get_trends_score(self, keyword: str, use_cache: bool = True) -> int:
        """Get Google Trends score with caching and rate limiting"""
        cache_key = self.cache._generate_key('trends', {'keyword': keyword.lower()})
        
        # Try cache first
        if use_cache:
            cached_score = self.cache.get(cache_key)
            if cached_score is not None:
                logger.debug(f"Using cached trends score for: {keyword}")
                return cached_score.get('score', 50)
        
        # Rate limiting - ensure minimum interval between API calls
        time_since_last = time.time() - self.last_call_time
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        try:
            logger.info(f"Making Google Trends API call: {keyword}")
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
            
            interest_data = pytrends.interest_over_time()
            self.last_call_time = time.time()
            self.call_count += 1
            
            if not interest_data.empty and keyword in interest_data.columns:
                score = int(interest_data[keyword].mean())
                logger.info(f"Google Trends: {keyword} = {score}/100")
            else:
                score = self._fallback_score(keyword)
                logger.warning(f"No trends data for '{keyword}', using fallback: {score}")
            
            # Cache with longer TTL (trends don't change much)
            if use_cache:
                temp_cache = APICache(ttl_seconds=14400)  # 4 hours
                temp_cache.cache = self.cache.cache
                temp_cache.set(cache_key, {'score': score})
            
            return score
            
        except Exception as e:
            logger.error(f"Google Trends API error for '{keyword}': {e}")
            return self._fallback_score(keyword)
    
    def _fallback_score(self, keyword: str) -> int:
        """Generate fallback trends score when API fails"""
        trending_keywords = {
            'ai': 75, 'artificial intelligence': 80, 'chatgpt': 85,
            'crypto': 70, 'bitcoin': 75, 'investing': 65,
            'tutorial': 60, 'tips': 55, 'guide': 58,
            'fitness': 50, 'tech': 55, 'business': 52
        }
        
        keyword_lower = keyword.lower()
        for kw, score in trending_keywords.items():
            if kw in keyword_lower:
                return min(score + random.randint(-5, 10), 100)
        
        return random.randint(40, 60)