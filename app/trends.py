"""
Google Trends API Module for YouTube Niche Discovery Engine

This module provides Google Trends integration using pytrends library
with caching and rate limiting to analyze keyword popularity over time.

Includes trend direction detection using:
- Linear regression (numpy polyfit) for slope calculation
- Period comparison (first-half vs second-half)
- Momentum calculation (recent vs average)
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from pytrends.request import TrendReq

from .cache import APICache

logger = logging.getLogger(__name__)


def calculate_trend_direction(values: List[float]) -> Dict[str, Any]:
    """
    Calculate trend direction using linear regression slope.
    
    Uses numpy polyfit to fit a line and determine direction.
    
    Args:
        values: List of trend values (typically 0-100 scale)
        
    Returns:
        Dict with:
        - slope: Raw slope value (positive = rising, negative = falling)
        - direction: 'rising', 'falling', or 'stable'
        - strength: 0-100 indicating how strong the trend is
        - r_squared: Goodness of fit (0-1)
    """
    if not values or len(values) < 2:
        return {
            'slope': 0.0,
            'direction': 'stable',
            'strength': 0.0,
            'r_squared': 0.0
        }
    
    # Filter out None/NaN values
    clean_values = [v for v in values if v is not None and not np.isnan(v)]
    if len(clean_values) < 2:
        return {
            'slope': 0.0,
            'direction': 'stable',
            'strength': 0.0,
            'r_squared': 0.0
        }
    
    x = np.arange(len(clean_values))
    y = np.array(clean_values)
    
    # Linear regression using polyfit (degree 1)
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    
    # Calculate R-squared for confidence
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    # Normalize slope to percentage per data point
    # Slope of 1 means +1 point per time unit
    normalized_slope = slope / max(np.mean(y), 1) * 100
    
    # Determine direction with thresholds
    if normalized_slope > 0.5:  # >0.5% per time unit = rising
        direction = 'rising'
    elif normalized_slope < -0.5:  # <-0.5% per time unit = falling
        direction = 'falling'
    else:
        direction = 'stable'
    
    # Strength is absolute normalized slope, capped at 100
    strength = min(abs(normalized_slope) * 10, 100)
    
    return {
        'slope': float(slope),
        'direction': direction,
        'strength': float(strength),
        'r_squared': float(max(0, min(1, r_squared)))
    }


def compare_periods(values: List[float]) -> Dict[str, Any]:
    """
    Compare first-half vs second-half of trend data.
    
    This provides a simple but robust measure of whether
    interest is growing or declining.
    
    Args:
        values: List of trend values
        
    Returns:
        Dict with:
        - first_half_avg: Average of first half
        - second_half_avg: Average of second half
        - change_percent: Percentage change (positive = growth)
        - direction: 'rising', 'falling', or 'stable'
    """
    if not values or len(values) < 4:
        return {
            'first_half_avg': 0.0,
            'second_half_avg': 0.0,
            'change_percent': 0.0,
            'direction': 'stable'
        }
    
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < 4:
        return {
            'first_half_avg': 0.0,
            'second_half_avg': 0.0,
            'change_percent': 0.0,
            'direction': 'stable'
        }
    
    midpoint = len(clean_values) // 2
    first_half = clean_values[:midpoint]
    second_half = clean_values[midpoint:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    if first_avg > 0:
        change_percent = ((second_avg - first_avg) / first_avg) * 100
    else:
        change_percent = 0.0 if second_avg == 0 else 100.0
    
    # Threshold: ±10% for stable
    if change_percent > 10:
        direction = 'rising'
    elif change_percent < -10:
        direction = 'falling'
    else:
        direction = 'stable'
    
    return {
        'first_half_avg': float(first_avg),
        'second_half_avg': float(second_avg),
        'change_percent': float(change_percent),
        'direction': direction
    }


def calculate_momentum(values: List[float], recent_window: int = 4) -> Dict[str, Any]:
    """
    Calculate momentum by comparing recent values to overall average.
    
    Args:
        values: List of trend values
        recent_window: Number of recent data points to consider
        
    Returns:
        Dict with:
        - recent_avg: Average of recent values
        - overall_avg: Overall average
        - momentum_score: -100 to +100 (positive = above average momentum)
        - direction: 'accelerating', 'decelerating', or 'stable'
    """
    if not values or len(values) < recent_window + 1:
        return {
            'recent_avg': 0.0,
            'overall_avg': 0.0,
            'momentum_score': 0.0,
            'direction': 'stable'
        }
    
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < recent_window + 1:
        return {
            'recent_avg': 0.0,
            'overall_avg': 0.0,
            'momentum_score': 0.0,
            'direction': 'stable'
        }
    
    recent_values = clean_values[-recent_window:]
    recent_avg = sum(recent_values) / len(recent_values)
    overall_avg = sum(clean_values) / len(clean_values)
    
    if overall_avg > 0:
        momentum_score = ((recent_avg - overall_avg) / overall_avg) * 100
    else:
        momentum_score = 0.0
    
    # Clamp to -100 to +100
    momentum_score = max(-100, min(100, momentum_score))
    
    # Threshold: ±15% for stable
    if momentum_score > 15:
        direction = 'accelerating'
    elif momentum_score < -15:
        direction = 'decelerating'
    else:
        direction = 'stable'
    
    return {
        'recent_avg': float(recent_avg),
        'overall_avg': float(overall_avg),
        'momentum_score': float(momentum_score),
        'direction': direction
    }


def analyze_trend_data(values: List[float]) -> Dict[str, Any]:
    """
    Comprehensive trend analysis combining all methods.
    
    Returns a unified analysis with direction-aware scoring.
    
    Args:
        values: List of trend values (0-100 scale from Google Trends)
        
    Returns:
        Dict with full trend analysis including:
        - base_score: Average value
        - adjusted_score: Direction-adjusted score (rising gets bonus, falling penalty)
        - direction: Overall direction ('rising', 'falling', 'stable')
        - confidence: How confident we are in the direction (0-100)
        - regression: Linear regression results
        - period_comparison: First vs second half comparison
        - momentum: Recent momentum analysis
    """
    if not values:
        return {
            'base_score': 50.0,
            'adjusted_score': 50.0,
            'direction': 'stable',
            'confidence': 0.0,
            'regression': calculate_trend_direction([]),
            'period_comparison': compare_periods([]),
            'momentum': calculate_momentum([])
        }
    
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return {
            'base_score': 50.0,
            'adjusted_score': 50.0,
            'direction': 'stable',
            'confidence': 0.0,
            'regression': calculate_trend_direction([]),
            'period_comparison': compare_periods([]),
            'momentum': calculate_momentum([])
        }
    
    # Calculate base score (average)
    base_score = sum(clean_values) / len(clean_values)
    
    # Get all trend analyses
    regression = calculate_trend_direction(clean_values)
    period_comp = compare_periods(clean_values)
    momentum = calculate_momentum(clean_values)
    
    # Determine overall direction by consensus
    directions = [regression['direction'], period_comp['direction']]
    if momentum['direction'] == 'accelerating':
        directions.append('rising')
    elif momentum['direction'] == 'decelerating':
        directions.append('falling')
    else:
        directions.append('stable')
    
    rising_votes = sum(1 for d in directions if d == 'rising')
    falling_votes = sum(1 for d in directions if d == 'falling')
    
    if rising_votes > falling_votes:
        overall_direction = 'rising'
    elif falling_votes > rising_votes:
        overall_direction = 'falling'
    else:
        overall_direction = 'stable'
    
    # Calculate confidence based on agreement and R-squared
    agreement = max(rising_votes, falling_votes, 3 - rising_votes - falling_votes) / 3
    r_squared_factor = regression['r_squared']
    confidence = (agreement * 0.6 + r_squared_factor * 0.4) * 100
    
    # Calculate direction-adjusted score
    # Rising trends get a bonus, falling trends get a penalty
    adjustment = 0.0
    if overall_direction == 'rising':
        # Bonus: up to +20% based on strength and confidence
        adjustment = min(20, regression['strength'] * 0.2) * (confidence / 100)
    elif overall_direction == 'falling':
        # Penalty: up to -20% based on strength and confidence
        adjustment = -min(20, regression['strength'] * 0.2) * (confidence / 100)
    
    adjusted_score = max(0, min(100, base_score + adjustment))
    
    return {
        'base_score': float(base_score),
        'adjusted_score': float(adjusted_score),
        'direction': overall_direction,
        'confidence': float(confidence),
        'regression': regression,
        'period_comparison': period_comp,
        'momentum': momentum
    }


class TrendsAPI:
    """Google Trends API with caching, rate limiting, and direction detection"""
    
    def __init__(self, cache: APICache):
        self.cache = cache
        self.call_count = 0
        self.last_call_time = 0
        self.min_interval = 1.0  # Minimum 1 second between calls
        self._last_known_scores: Dict[str, int] = {}  # Track last known values for fallback
        logger.info("TrendsAPI initialized")
    
    def get_trends_score(self, keyword: str, use_cache: bool = True) -> int:
        """Get Google Trends score with caching and rate limiting (simple API)"""
        result = self.get_trends_data(keyword, use_cache)
        return result.get('score', 50)
    
    def get_trends_data(self, keyword: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive Google Trends data with direction detection.
        
        Returns:
            Dict with:
            - score: Direction-adjusted score (0-100)
            - base_score: Raw average score
            - direction: 'rising', 'falling', or 'stable'
            - direction_confidence: How confident we are (0-100)
            - period_change: Percentage change first-half to second-half
            - momentum: Recent momentum score (-100 to +100)
            - values: Raw trend values (for further analysis)
        """
        cache_key = self.cache._generate_key('trends', {'keyword': keyword.lower()})
        
        # Try cache first
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached trends data for: {keyword}")
                return cached_data
        
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
                values = interest_data[keyword].tolist()
                
                # Analyze trend direction
                analysis = analyze_trend_data(values)
                
                result = {
                    'score': int(analysis['adjusted_score']),
                    'base_score': int(analysis['base_score']),
                    'direction': analysis['direction'],
                    'direction_confidence': analysis['confidence'],
                    'period_change': analysis['period_comparison']['change_percent'],
                    'momentum': analysis['momentum']['momentum_score'],
                    'slope': analysis['regression']['slope'],
                    'values': values
                }
                
                # Store last known score for fallback
                self._last_known_scores[keyword.lower()] = result['score']
                
                direction_str = f"{'↑' if analysis['direction'] == 'rising' else '↓' if analysis['direction'] == 'falling' else '→'}"
                logger.info(f"Google Trends: {keyword} = {result['score']}/100 {direction_str} "
                           f"(base:{result['base_score']}, dir:{analysis['direction']}, "
                           f"conf:{analysis['confidence']:.0f}%)")
            else:
                result = self._fallback_data(keyword)
                logger.warning(f"No trends data for '{keyword}', using fallback: {result['score']}")
            
            # Cache with longer TTL (trends don't change much)
            if use_cache:
                temp_cache = APICache(ttl_seconds=14400)  # 4 hours
                temp_cache.cache = self.cache.cache
                temp_cache.set(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Google Trends API error for '{keyword}': {e}")
            return self._fallback_data(keyword)
    
    def _fallback_data(self, keyword: str) -> Dict[str, Any]:
        """
        Generate fallback trends data when API fails.
        Uses last known value or category-based estimate. NO random values.
        """
        keyword_lower = keyword.lower()
        
        # First, check if we have a last known value
        if keyword_lower in self._last_known_scores:
            last_score = self._last_known_scores[keyword_lower]
            logger.debug(f"Using last known score for '{keyword}': {last_score}")
            return {
                'score': last_score,
                'base_score': last_score,
                'direction': 'stable',  # Can't determine direction without data
                'direction_confidence': 0.0,
                'period_change': 0.0,
                'momentum': 0.0,
                'slope': 0.0,
                'values': [],
                'is_fallback': True
            }
        
        # Category-based estimates (deterministic, no randomness)
        trending_keywords = {
            'ai': 75, 'artificial intelligence': 80, 'chatgpt': 85,
            'crypto': 70, 'bitcoin': 75, 'investing': 65,
            'tutorial': 60, 'tips': 55, 'guide': 58,
            'fitness': 50, 'tech': 55, 'business': 52,
            'gaming': 65, 'cooking': 48, 'travel': 45,
            'music': 55, 'finance': 60, 'health': 52
        }
        
        # Check for keyword matches
        for kw, score in trending_keywords.items():
            if kw in keyword_lower:
                return {
                    'score': score,
                    'base_score': score,
                    'direction': 'stable',
                    'direction_confidence': 0.0,
                    'period_change': 0.0,
                    'momentum': 0.0,
                    'slope': 0.0,
                    'values': [],
                    'is_fallback': True
                }
        
        # Ultimate fallback: neutral score of 50 (not random)
        return {
            'score': 50,
            'base_score': 50,
            'direction': 'stable',
            'direction_confidence': 0.0,
            'period_change': 0.0,
            'momentum': 0.0,
            'slope': 0.0,
            'values': [],
            'is_fallback': True
        }