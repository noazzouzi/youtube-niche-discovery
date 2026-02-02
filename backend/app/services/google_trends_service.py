"""
Google Trends Service - Search trend analysis for niche discovery
Implements Google Trends integration for PM Agent's 100-point scoring algorithm
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json

from pytrends.request import TrendReq
from app.models.metric import Metric

logger = logging.getLogger(__name__)

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
            
            # 2. Get current trending score
            trending_score = await self._get_trending_score(search_terms[0])
            if trending_score is not None:
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=2,  # Google Trends source
                    metric_type="search_volume",
                    metric_name="google_trends_score",
                    value=trending_score,
                    period="current",
                    confidence_score=95.0,  # Google Trends is very reliable
                    collected_at=datetime.utcnow()
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
    
    async def _get_trending_score(self, keyword: str) -> Optional[float]:
        """Get current trending score (0-100) for a keyword"""
        try:
            # Get recent trend data (last 3 months)
            trend_data = await self._get_interest_over_time([keyword], timeframe='today 3-m')
            
            if trend_data and keyword in trend_data.get("values", {}):
                values = trend_data["values"][keyword]
                
                if values and len(values) > 0:
                    # Calculate trending score based on recent average
                    recent_values = [v for v in values if v is not None]
                    if recent_values:
                        avg_score = sum(recent_values) / len(recent_values)
                        return float(avg_score)
            
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
        Discover trending keywords that could become niches
        """
        trending_keywords = []
        
        try:
            # Get trending searches (this is a simplified version)
            # In practice, you might want to use Google Trends' trending searches API
            # or analyze rising topics across multiple categories
            
            sample_keywords = [
                "AI tools", "passive income", "crypto trading", "home workout",
                "sustainable living", "digital nomad", "mindfulness", "plant care",
                "tech reviews", "cooking hacks", "productivity tips", "finance tips"
            ]
            
            for keyword in sample_keywords:
                try:
                    trending_score = await self._get_trending_score(keyword)
                    
                    if trending_score and trending_score > 20:  # Minimum threshold
                        trending_keywords.append({
                            "keyword": keyword,
                            "trending_score": trending_score,
                            "discovery_source": "google_trends",
                            "category": category or "general"
                        })
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error checking keyword '{keyword}': {e}")
                    continue
            
            # Sort by trending score
            trending_keywords.sort(key=lambda x: x["trending_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error discovering trending keywords: {e}")
        
        return trending_keywords