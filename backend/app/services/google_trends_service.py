"""
Google Trends Service - Search trend analysis for niche discovery
Implements Google Trends integration for PM Agent's 100-point scoring algorithm

Includes direction-aware trend detection:
- Linear regression for slope calculation
- Period comparison (first-half vs second-half)
- Momentum calculation (recent vs average)
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json
import numpy as np

from pytrends.request import TrendReq
from app.models.metric import Metric

logger = logging.getLogger(__name__)


def _calculate_trend_direction(values: List[float]) -> Dict[str, Any]:
    """Calculate trend direction using linear regression slope (numpy polyfit)."""
    if not values or len(values) < 2:
        return {'slope': 0.0, 'direction': 'stable', 'strength': 0.0, 'r_squared': 0.0}
    
    clean_values = [v for v in values if v is not None and not np.isnan(v)]
    if len(clean_values) < 2:
        return {'slope': 0.0, 'direction': 'stable', 'strength': 0.0, 'r_squared': 0.0}
    
    x = np.arange(len(clean_values))
    y = np.array(clean_values)
    
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    
    y_pred = np.polyval(coeffs, x)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    normalized_slope = slope / max(np.mean(y), 1) * 100
    
    if normalized_slope > 0.5:
        direction = 'rising'
    elif normalized_slope < -0.5:
        direction = 'falling'
    else:
        direction = 'stable'
    
    return {
        'slope': float(slope),
        'direction': direction,
        'strength': min(abs(normalized_slope) * 10, 100),
        'r_squared': float(max(0, min(1, r_squared)))
    }


def _compare_periods(values: List[float]) -> Dict[str, Any]:
    """Compare first-half vs second-half of trend data."""
    if not values or len(values) < 4:
        return {'first_half_avg': 0.0, 'second_half_avg': 0.0, 'change_percent': 0.0, 'direction': 'stable'}
    
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < 4:
        return {'first_half_avg': 0.0, 'second_half_avg': 0.0, 'change_percent': 0.0, 'direction': 'stable'}
    
    midpoint = len(clean_values) // 2
    first_avg = sum(clean_values[:midpoint]) / midpoint
    second_avg = sum(clean_values[midpoint:]) / (len(clean_values) - midpoint)
    
    change_percent = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0.0
    
    if change_percent > 10:
        direction = 'rising'
    elif change_percent < -10:
        direction = 'falling'
    else:
        direction = 'stable'
    
    return {
        'first_half_avg': first_avg,
        'second_half_avg': second_avg,
        'change_percent': change_percent,
        'direction': direction
    }


def _calculate_momentum(values: List[float], recent_window: int = 4) -> Dict[str, Any]:
    """Calculate momentum by comparing recent values to overall average."""
    if not values or len(values) < recent_window + 1:
        return {'recent_avg': 0.0, 'overall_avg': 0.0, 'momentum_score': 0.0, 'direction': 'stable'}
    
    clean_values = [v for v in values if v is not None]
    if len(clean_values) < recent_window + 1:
        return {'recent_avg': 0.0, 'overall_avg': 0.0, 'momentum_score': 0.0, 'direction': 'stable'}
    
    recent_avg = sum(clean_values[-recent_window:]) / recent_window
    overall_avg = sum(clean_values) / len(clean_values)
    
    momentum_score = ((recent_avg - overall_avg) / overall_avg * 100) if overall_avg > 0 else 0.0
    momentum_score = max(-100, min(100, momentum_score))
    
    if momentum_score > 15:
        direction = 'accelerating'
    elif momentum_score < -15:
        direction = 'decelerating'
    else:
        direction = 'stable'
    
    return {
        'recent_avg': recent_avg,
        'overall_avg': overall_avg,
        'momentum_score': momentum_score,
        'direction': direction
    }

class GoogleTrendsService:
    """
    Google Trends service for niche discovery scoring
    
    Provides data for:
    - Search Volume Score (15 points of 25 total)
    - Trend Momentum Score (10 points of 15 total)
    - Geographic and demographic insights
    """
    
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self.rate_limit_delay = 2.0  # Seconds between requests to avoid blocking
        
    async def collect_niche_trends_metrics(self, niche_id: int, niche_name: str, keywords: List[str]) -> List[Metric]:
        """
        Collect Google Trends metrics for niche scoring
        
        Returns metrics for:
        - google_trends_score (0-100 scale)
        - twelve_month_growth (percentage)
        - regional_interest (geographic data)
        - related_queries (content opportunities)
        """
        metrics = []
        
        try:
            # Prepare search terms (Google Trends allows max 5 terms per request)
            search_terms = [niche_name] + keywords[:4]
            search_terms = [term for term in search_terms if len(term) > 2][:5]
            
            if not search_terms:
                logger.warning(f"No valid search terms for niche {niche_name}")
                return metrics
            
            # 1. Get interest over time (trend momentum)
            trend_data = await self._get_interest_over_time(search_terms)
            if trend_data:
                trend_metrics = self._create_trend_metrics(niche_id, trend_data, search_terms[0])
                metrics.extend(trend_metrics)
            
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # 2. Get current trending score with direction detection
            trending_data = await self._get_trending_score(search_terms[0])
            if trending_data is not None:
                # Main trending score (direction-adjusted)
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=2,  # Google Trends source
                    metric_type="search_volume",
                    metric_name="google_trends_score",
                    value=trending_data['score'],
                    period="current",
                    confidence_score=95.0,
                    collected_at=datetime.utcnow(),
                    raw_data=json.dumps({
                        'base_score': trending_data['base_score'],
                        'direction': trending_data['direction'],
                        'direction_confidence': trending_data['direction_confidence']
                    })
                ))
                
                # Trend direction metric for scoring
                direction_value = 0  # stable
                if trending_data['direction'] == 'rising':
                    direction_value = 1
                elif trending_data['direction'] == 'falling':
                    direction_value = -1
                    
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=2,
                    metric_type="trend_momentum",
                    metric_name="trend_direction",
                    value=direction_value,
                    period="current",
                    confidence_score=trending_data['direction_confidence'],
                    collected_at=datetime.utcnow(),
                    raw_data=json.dumps({
                        'direction': trending_data['direction'],
                        'period_change': trending_data['period_change'],
                        'momentum': trending_data['momentum'],
                        'slope': trending_data['slope']
                    })
                ))
            
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # 3. Get related queries for content opportunities
            related_data = await self._get_related_queries(search_terms[0])
            if related_data:
                content_score = self._calculate_content_opportunity_score(related_data)
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=2,
                    metric_type="content_opportunity", 
                    metric_name="related_topics_score",
                    value=content_score,
                    period="current",
                    confidence_score=85.0,
                    collected_at=datetime.utcnow(),
                    raw_data=json.dumps(related_data[:20])  # Store top 20 related queries
                ))
            
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # 4. Get geographic interest
            geo_data = await self._get_geographic_interest(search_terms[0])
            if geo_data:
                geo_score = self._calculate_geographic_score(geo_data)
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=2,
                    metric_type="market_analysis",
                    metric_name="geographic_interest_score",
                    value=geo_score,
                    period="current",
                    confidence_score=80.0,
                    collected_at=datetime.utcnow(),
                    raw_data=json.dumps(geo_data[:10])
                ))
            
            logger.info(f"Collected {len(metrics)} Google Trends metrics for niche '{niche_name}'")
            
        except Exception as e:
            logger.error(f"Error collecting Google Trends metrics for '{niche_name}': {e}")
        
        return metrics
    
    async def _get_interest_over_time(self, keywords: List[str], timeframe: str = 'today 12-m') -> Optional[Dict[str, Any]]:
        """Get search interest over time for trend analysis"""
        try:
            # Run in thread pool since pytrends is synchronous
            loop = asyncio.get_event_loop()
            
            def _fetch_trends():
                try:
                    self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo='US', gprop='')
                    data = self.pytrends.interest_over_time()
                    return data
                except Exception as e:
                    logger.error(f"Error fetching trends data: {e}")
                    return None
            
            data = await loop.run_in_executor(None, _fetch_trends)
            
            if data is not None and not data.empty:
                # Convert to JSON-serializable format
                trend_data = {
                    "dates": [d.isoformat() for d in data.index],
                    "values": {}
                }
                
                for keyword in keywords:
                    if keyword in data.columns:
                        trend_data["values"][keyword] = data[keyword].tolist()
                
                return trend_data
            
        except Exception as e:
            logger.error(f"Error getting interest over time: {e}")
        
        return None
    
    async def _get_trending_score(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Get current trending score with direction detection.
        
        Returns:
            Dict with:
            - score: Direction-adjusted score (0-100)
            - base_score: Raw average
            - direction: 'rising', 'falling', or 'stable'
            - direction_confidence: Confidence in direction (0-100)
            - period_change: YoY-style percentage change
            - momentum: Recent momentum score
        """
        try:
            # Get recent trend data (last 3 months for current state)
            trend_data = await self._get_interest_over_time([keyword], timeframe='today 3-m')
            
            if trend_data and keyword in trend_data.get("values", {}):
                values = trend_data["values"][keyword]
                clean_values = [v for v in values if v is not None]
                
                if clean_values and len(clean_values) > 0:
                    # Calculate base score
                    base_score = sum(clean_values) / len(clean_values)
                    
                    # Get direction analysis
                    regression = _calculate_trend_direction(clean_values)
                    period_comp = _compare_periods(clean_values)
                    momentum = _calculate_momentum(clean_values)
                    
                    # Determine overall direction
                    directions = [regression['direction'], period_comp['direction']]
                    if momentum['direction'] == 'accelerating':
                        directions.append('rising')
                    elif momentum['direction'] == 'decelerating':
                        directions.append('falling')
                    else:
                        directions.append('stable')
                    
                    rising = sum(1 for d in directions if d == 'rising')
                    falling = sum(1 for d in directions if d == 'falling')
                    
                    if rising > falling:
                        overall_direction = 'rising'
                    elif falling > rising:
                        overall_direction = 'falling'
                    else:
                        overall_direction = 'stable'
                    
                    # Calculate confidence
                    agreement = max(rising, falling, 3 - rising - falling) / 3
                    confidence = (agreement * 0.6 + regression['r_squared'] * 0.4) * 100
                    
                    # Adjust score based on direction
                    adjustment = 0.0
                    if overall_direction == 'rising':
                        adjustment = min(20, regression['strength'] * 0.2) * (confidence / 100)
                    elif overall_direction == 'falling':
                        adjustment = -min(20, regression['strength'] * 0.2) * (confidence / 100)
                    
                    adjusted_score = max(0, min(100, base_score + adjustment))
                    
                    logger.debug(f"Trend score for '{keyword}': {adjusted_score:.1f} "
                               f"(base:{base_score:.1f}, dir:{overall_direction}, conf:{confidence:.0f}%)")
                    
                    return {
                        'score': float(adjusted_score),
                        'base_score': float(base_score),
                        'direction': overall_direction,
                        'direction_confidence': float(confidence),
                        'period_change': float(period_comp['change_percent']),
                        'momentum': float(momentum['momentum_score']),
                        'slope': float(regression['slope'])
                    }
            
        except Exception as e:
            logger.error(f"Error calculating trending score: {e}")
        
        return None
    
    async def _get_related_queries(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """Get related queries for content opportunity analysis"""
        try:
            loop = asyncio.get_event_loop()
            
            def _fetch_related():
                try:
                    self.pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='US', gprop='')
                    related = self.pytrends.related_queries()
                    return related
                except Exception as e:
                    logger.error(f"Error fetching related queries: {e}")
                    return None
            
            related_data = await loop.run_in_executor(None, _fetch_related)
            
            if related_data and keyword in related_data:
                # Extract top rising queries
                rising = related_data[keyword].get('rising')
                top = related_data[keyword].get('top')
                
                all_queries = []
                
                if rising is not None and not rising.empty:
                    for idx, row in rising.head(10).iterrows():
                        all_queries.append({
                            "query": row['query'],
                            "value": row['value'],
                            "type": "rising"
                        })
                
                if top is not None and not top.empty:
                    for idx, row in top.head(10).iterrows():
                        all_queries.append({
                            "query": row['query'],
                            "value": row['value'],
                            "type": "top"
                        })
                
                return all_queries
            
        except Exception as e:
            logger.error(f"Error getting related queries: {e}")
        
        return None
    
    async def _get_geographic_interest(self, keyword: str) -> Optional[List[Dict[str, Any]]]:
        """Get geographic distribution of search interest"""
        try:
            loop = asyncio.get_event_loop()
            
            def _fetch_geo():
                try:
                    self.pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='', gprop='')
                    geo_data = self.pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
                    return geo_data
                except Exception as e:
                    logger.error(f"Error fetching geographic data: {e}")
                    return None
            
            geo_data = await loop.run_in_executor(None, _fetch_geo)
            
            if geo_data is not None and not geo_data.empty:
                geo_list = []
                for country, value in geo_data[keyword].head(20).items():
                    if value > 0:  # Filter out zero values
                        geo_list.append({
                            "country": country,
                            "interest": int(value)
                        })
                
                return geo_list
            
        except Exception as e:
            logger.error(f"Error getting geographic interest: {e}")
        
        return None
    
    def _create_trend_metrics(self, niche_id: int, trend_data: Dict[str, Any], primary_keyword: str) -> List[Metric]:
        """Create trend-related metrics from interest over time data"""
        metrics = []
        
        try:
            if primary_keyword in trend_data.get("values", {}):
                values = trend_data["values"][primary_keyword]
                dates = trend_data["dates"]
                
                # Filter out None values
                valid_data = [(d, v) for d, v in zip(dates, values) if v is not None]
                
                if len(valid_data) >= 4:  # Need minimum data points
                    values_only = [v for _, v in valid_data]
                    
                    # Calculate 12-month growth
                    if len(values_only) >= 12:
                        recent_avg = sum(values_only[-4:]) / 4  # Last month average
                        old_avg = sum(values_only[:4]) / 4     # First month average
                        
                        if old_avg > 0:
                            growth_rate = ((recent_avg - old_avg) / old_avg) * 100
                            
                            metrics.append(Metric(
                                niche_id=niche_id,
                                source_id=2,
                                metric_type="trend_momentum",
                                metric_name="twelve_month_growth",
                                value=growth_rate,
                                period="12_months",
                                confidence_score=90.0,
                                collected_at=datetime.utcnow()
                            ))
                    
                    # Calculate trend volatility
                    if len(values_only) > 1:
                        avg_value = sum(values_only) / len(values_only)
                        variance = sum((v - avg_value) ** 2 for v in values_only) / len(values_only)
                        volatility = (variance ** 0.5) / max(avg_value, 1) * 100
                        
                        metrics.append(Metric(
                            niche_id=niche_id,
                            source_id=2,
                            metric_type="trend_momentum",
                            metric_name="trend_volatility",
                            value=min(volatility, 100),  # Cap at 100
                            period="12_months",
                            confidence_score=85.0,
                            collected_at=datetime.utcnow()
                        ))
        
        except Exception as e:
            logger.error(f"Error creating trend metrics: {e}")
        
        return metrics
    
    def _calculate_content_opportunity_score(self, related_queries: List[Dict[str, Any]]) -> float:
        """Calculate content opportunity score based on related queries"""
        try:
            if not related_queries:
                return 0.0
            
            # Score based on number and quality of related queries
            rising_count = len([q for q in related_queries if q.get('type') == 'rising'])
            total_count = len(related_queries)
            
            # Rising queries indicate growing interest and content opportunities
            rising_weight = 2.0
            base_score = (rising_count * rising_weight + (total_count - rising_count)) * 5
            
            # Bonus for high-value queries
            high_value_count = len([q for q in related_queries if q.get('value', 0) > 50])
            bonus = high_value_count * 10
            
            total_score = min(base_score + bonus, 100)  # Cap at 100
            return total_score
        
        except Exception as e:
            logger.error(f"Error calculating content opportunity score: {e}")
            return 0.0
    
    def _calculate_geographic_score(self, geo_data: List[Dict[str, Any]]) -> float:
        """Calculate geographic distribution score for market potential"""
        try:
            if not geo_data:
                return 0.0
            
            # Score based on geographic diversity and high-value markets
            high_cpm_countries = ['United States', 'Australia', 'Switzerland', 'Germany', 'United Kingdom', 'Canada']
            
            total_interest = sum(item.get('interest', 0) for item in geo_data)
            high_cpm_interest = sum(item.get('interest', 0) for item in geo_data 
                                  if item.get('country') in high_cpm_countries)
            
            # Calculate scores
            diversity_score = min(len(geo_data) * 5, 50)  # Max 50 for diversity
            quality_score = (high_cpm_interest / max(total_interest, 1)) * 50  # Max 50 for quality
            
            return diversity_score + quality_score
        
        except Exception as e:
            logger.error(f"Error calculating geographic score: {e}")
            return 0.0

    async def discover_trending_keywords(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover trending keywords that could become niches.
        Now includes direction detection to prioritize rising trends.
        """
        trending_keywords = []
        
        try:
            # Sample keywords (in practice, use Google Trends trending searches API)
            sample_keywords = [
                "AI tools", "passive income", "crypto trading", "home workout",
                "sustainable living", "digital nomad", "mindfulness", "plant care",
                "tech reviews", "cooking hacks", "productivity tips", "finance tips"
            ]
            
            for keyword in sample_keywords:
                try:
                    trending_data = await self._get_trending_score(keyword)
                    
                    if trending_data and trending_data.get('score', 0) > 20:
                        trending_keywords.append({
                            "keyword": keyword,
                            "trending_score": trending_data['score'],
                            "base_score": trending_data.get('base_score', trending_data['score']),
                            "direction": trending_data.get('direction', 'stable'),
                            "direction_confidence": trending_data.get('direction_confidence', 0),
                            "momentum": trending_data.get('momentum', 0),
                            "discovery_source": "google_trends",
                            "category": category or "general"
                        })
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error checking keyword '{keyword}': {e}")
                    continue
            
            # Sort by trending score, with rising trends getting priority
            # Rising trends with same score should rank higher than falling
            def sort_key(x):
                direction_bonus = {'rising': 10, 'stable': 0, 'falling': -10}
                return x["trending_score"] + direction_bonus.get(x.get("direction", "stable"), 0)
            
            trending_keywords.sort(key=sort_key, reverse=True)
            
        except Exception as e:
            logger.error(f"Error discovering trending keywords: {e}")
        
        return trending_keywords