"""
YouTube Service - Complete API integration for niche discovery scoring
Implements data collection for PM Agent's 100-point scoring algorithm
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import json
import asyncio
from datetime import datetime, timedelta
import re
import aiohttp
import math

from .base_scraper import BaseScraper
from app.core.config import settings
from app.models.metric import Metric
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class YouTubeService(BaseScraper):
    """
    Complete YouTube data service for niche discovery and scoring
    
    Collects data for PM Agent's 100-point algorithm:
    - YouTube search volume (10 points of Search Volume)
    - Channel saturation analysis (15 points of Competition)
    - Subscriber growth rates (10 points of Competition) 
    - Content opportunity analysis (part of Content Availability)
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__("youtube", session)
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_api_url = "https://www.googleapis.com/youtube/v3"
        
        # API quota management
        self.quota_used = 0
        self.quota_limit = 10000  # Daily free tier limit
        
        # Cost per API call (quota units)
        self.quota_costs = {
            "search": 100,
            "videos": 1,
            "channels": 1,
            "playlists": 1
        }
        
        # Category CPM estimates for monetization scoring
        self.category_cpm_estimates = {
            "2": 2.5,   # Autos & Vehicles
            "1": 2.0,   # Film & Animation
            "10": 1.0,  # Music
            "15": 2.0,  # Pets & Animals
            "17": 2.5,  # Sports
            "19": 3.0,  # Travel & Events
            "20": 3.0,  # Gaming
            "22": 2.0,  # People & Blogs
            "23": 1.5,  # Comedy
            "24": 2.0,  # Entertainment
            "25": 4.0,  # News & Politics
            "26": 3.5,  # Howto & Style
            "27": 5.0,  # Education
            "28": 4.5,  # Science & Technology
        }
    
    async def collect_niche_metrics(self, niche_name: str, niche_id: int) -> List[Metric]:
        """
        Collect comprehensive metrics for a niche based on PM algorithm requirements
        
        Returns metrics for:
        - youtube_monthly_searches (for Search Volume scoring)
        - channels_per_million_searches (for Competition scoring)
        - avg_monthly_subscriber_growth (for Competition scoring)
        - estimated_cpm (for Monetization scoring)
        """
        if not self.api_key:
            logger.warning("YouTube API key not configured - using estimates")
            return self._generate_estimated_metrics(niche_name, niche_id)
        
        metrics = []
        
        try:
            # 1. Search Volume Analysis
            search_volume_metrics = await self._analyze_search_volume(niche_name, niche_id)
            metrics.extend(search_volume_metrics)
            
            # 2. Competition Analysis
            competition_metrics = await self._analyze_competition(niche_name, niche_id)
            metrics.extend(competition_metrics)
            
            # 3. Channel Growth Analysis  
            growth_metrics = await self._analyze_channel_growth(niche_name, niche_id)
            metrics.extend(growth_metrics)
            
            # 4. Monetization Analysis
            monetization_metrics = await self._analyze_monetization(niche_name, niche_id)
            metrics.extend(monetization_metrics)
            
            logger.info(f"Collected {len(metrics)} YouTube metrics for niche: {niche_name}")
            
        except Exception as e:
            logger.error(f"Error collecting YouTube metrics for {niche_name}: {e}")
            metrics = self._generate_estimated_metrics(niche_name, niche_id)
        
        return metrics
    
    async def _analyze_search_volume(self, niche_name: str, niche_id: int) -> List[Metric]:
        """Analyze search volume for PM algorithm (10 points contribution)"""
        metrics = []
        
        try:
            # Search for videos in this niche
            search_results = await self._search_videos(niche_name, max_results=50)
            
            if not search_results:
                # Fallback estimate
                estimated_searches = await self._estimate_search_volume(niche_name)
                metrics.append(Metric(
                    niche_id=niche_id,
                    metric_type="youtube_monthly_searches",
                    value=estimated_searches,
                    unit="count",
                    confidence_score=50.0,
                    collected_at=datetime.utcnow(),
                    source_platform="youtube"
                ))
                return metrics
            
            # Analyze total result count and video performance
            total_results = len(search_results)
            
            # Estimate monthly search volume based on video count and performance
            avg_views = sum(int(self._get_video_stats(video_id).get("viewCount", 0)) 
                          for video_id in [item.get("id", {}).get("videoId", "") for item in search_results[:10]] 
                          if video_id) / min(10, len(search_results))
            
            # Rough estimation: views * search-to-view ratio
            estimated_monthly_searches = int(avg_views * total_results * 0.1)  # 10% CTR estimate
            
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="youtube_monthly_searches",
                value=estimated_monthly_searches,
                unit="count",
                confidence_score=70.0,
                collected_at=datetime.utcnow(),
                source_platform="youtube",
                metadata={"total_results": total_results, "avg_views": avg_views}
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing search volume: {e}")
            # Fallback
            estimated_searches = await self._estimate_search_volume(niche_name)
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="youtube_monthly_searches", 
                value=estimated_searches,
                unit="count",
                confidence_score=30.0,
                collected_at=datetime.utcnow(),
                source_platform="youtube"
            ))
        
        return metrics
    
    async def _analyze_competition(self, niche_name: str, niche_id: int) -> List[Metric]:
        """Analyze competition for PM algorithm (15 points contribution)"""
        metrics = []
        
        try:
            # Search for channels in this niche
            search_results = await self._search_videos(niche_name, max_results=50)
            
            if not search_results:
                # Fallback estimates
                metrics.append(Metric(
                    niche_id=niche_id,
                    metric_type="channels_per_million_searches",
                    value=150.0,  # Default middle value
                    unit="ratio",
                    confidence_score=30.0,
                    collected_at=datetime.utcnow(),
                    source_platform="youtube"
                ))
                return metrics
            
            # Extract unique channels
            unique_channels = set()
            for item in search_results:
                channel_id = item.get("snippet", {}).get("channelId")
                if channel_id:
                    unique_channels.add(channel_id)
            
            # Get estimated search volume for ratio calculation
            search_volume_metrics = await self._analyze_search_volume(niche_name, niche_id)
            estimated_searches = 100000  # Default
            if search_volume_metrics:
                estimated_searches = search_volume_metrics[0].value
            
            # Calculate channels per million searches
            channels_per_million = (len(unique_channels) / max(estimated_searches, 1)) * 1000000
            
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="channels_per_million_searches",
                value=round(channels_per_million, 2),
                unit="ratio",
                confidence_score=65.0,
                collected_at=datetime.utcnow(),
                source_platform="youtube",
                metadata={"unique_channels": len(unique_channels), "search_volume": estimated_searches}
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {e}")
        
        return metrics
    
    async def _analyze_channel_growth(self, niche_name: str, niche_id: int) -> List[Metric]:
        """Analyze channel growth rates for PM algorithm (10 points contribution)"""
        metrics = []
        
        try:
            # Get top channels in this niche
            search_results = await self._search_videos(niche_name, max_results=20)
            
            if not search_results:
                # Fallback estimate
                metrics.append(Metric(
                    niche_id=niche_id,
                    metric_type="avg_monthly_subscriber_growth",
                    value=15.0,  # Default middle value (10-20% range)
                    unit="percentage",
                    confidence_score=30.0,
                    collected_at=datetime.utcnow(),
                    source_platform="youtube"
                ))
                return metrics
            
            # Extract top channels and analyze their growth
            channel_ids = []
            for item in search_results[:10]:  # Top 10 channels
                channel_id = item.get("snippet", {}).get("channelId")
                if channel_id and channel_id not in channel_ids:
                    channel_ids.append(channel_id)
            
            # Get channel statistics
            growth_rates = []
            for channel_id in channel_ids[:5]:  # Limit API calls
                channel_stats = await self._get_channel_stats(channel_id)
                if channel_stats:
                    # Estimate growth based on subscriber count and channel age
                    subscriber_count = int(channel_stats.get("subscriberCount", 0))
                    published_at = channel_stats.get("publishedAt")
                    
                    if published_at and subscriber_count > 0:
                        # Calculate estimated monthly growth
                        channel_age_months = self._calculate_channel_age_months(published_at)
                        if channel_age_months > 0:
                            monthly_growth = (subscriber_count / channel_age_months) / max(subscriber_count, 1) * 100
                            growth_rates.append(min(monthly_growth, 100))  # Cap at 100%
            
            # Calculate average growth rate
            if growth_rates:
                avg_growth_rate = sum(growth_rates) / len(growth_rates)
                confidence = 70.0
            else:
                avg_growth_rate = 15.0  # Default estimate
                confidence = 30.0
            
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="avg_monthly_subscriber_growth",
                value=round(avg_growth_rate, 2),
                unit="percentage",
                confidence_score=confidence,
                collected_at=datetime.utcnow(),
                source_platform="youtube",
                metadata={"analyzed_channels": len(growth_rates)}
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing channel growth: {e}")
        
        return metrics
    
    async def _analyze_monetization(self, niche_name: str, niche_id: int) -> List[Metric]:
        """Analyze monetization potential for PM algorithm (15 points contribution)"""
        metrics = []
        
        try:
            # Get sample videos to determine category
            search_results = await self._search_videos(niche_name, max_results=10)
            
            # Collect category information
            categories = []
            for item in search_results:
                video_id = item.get("id", {}).get("videoId", "")
                if video_id:
                    video_stats = await self._get_video_stats(video_id)
                    category_id = video_stats.get("categoryId")
                    if category_id:
                        categories.append(category_id)
            
            # Estimate CPM based on category distribution
            estimated_cpm = self._calculate_estimated_cpm(categories, niche_name)
            
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="estimated_cpm",
                value=estimated_cpm,
                unit="currency",
                confidence_score=60.0,
                collected_at=datetime.utcnow(),
                source_platform="youtube",
                metadata={"categories_analyzed": categories}
            ))
            
        except Exception as e:
            logger.error(f"Error analyzing monetization: {e}")
            # Fallback estimate
            metrics.append(Metric(
                niche_id=niche_id,
                metric_type="estimated_cpm",
                value=3.0,  # Default middle CPM
                unit="currency",
                confidence_score=30.0,
                collected_at=datetime.utcnow(),
                source_platform="youtube"
            ))
        
        return metrics
    
    async def _search_videos(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for videos using YouTube Data API"""
        if not self.api_key:
            return []
        
        # Check quota
        if self.quota_used + self.quota_costs["search"] > self.quota_limit:
            logger.warning("YouTube API quota limit reached")
            return []
        
        url = f"{self.base_api_url}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),
            "order": "relevance",
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        self.quota_used += self.quota_costs["search"]
                        data = await response.json()
                        return data.get("items", [])
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error calling YouTube API: {e}")
                return []
    
    async def _get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics using YouTube Data API"""
        if not self.api_key or not video_id:
            return {}
        
        # Check quota
        if self.quota_used + self.quota_costs["videos"] > self.quota_limit:
            return {}
        
        url = f"{self.base_api_url}/videos"
        params = {
            "part": "snippet,statistics",
            "id": video_id,
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        self.quota_used += self.quota_costs["videos"]
                        data = await response.json()
                        items = data.get("items", [])
                        if items:
                            item = items[0]
                            stats = item.get("statistics", {})
                            snippet = item.get("snippet", {})
                            return {
                                "viewCount": stats.get("viewCount", "0"),
                                "likeCount": stats.get("likeCount", "0"),
                                "commentCount": stats.get("commentCount", "0"),
                                "categoryId": snippet.get("categoryId"),
                                "publishedAt": snippet.get("publishedAt")
                            }
                    return {}
            except Exception as e:
                logger.error(f"Error getting video stats: {e}")
                return {}
    
    async def _get_channel_stats(self, channel_id: str) -> Dict[str, Any]:
        """Get channel statistics using YouTube Data API"""
        if not self.api_key or not channel_id:
            return {}
        
        # Check quota
        if self.quota_used + self.quota_costs["channels"] > self.quota_limit:
            return {}
        
        url = f"{self.base_api_url}/channels"
        params = {
            "part": "snippet,statistics",
            "id": channel_id,
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        self.quota_used += self.quota_costs["channels"]
                        data = await response.json()
                        items = data.get("items", [])
                        if items:
                            item = items[0]
                            stats = item.get("statistics", {})
                            snippet = item.get("snippet", {})
                            return {
                                "subscriberCount": stats.get("subscriberCount", "0"),
                                "videoCount": stats.get("videoCount", "0"),
                                "viewCount": stats.get("viewCount", "0"),
                                "publishedAt": snippet.get("publishedAt")
                            }
                    return {}
            except Exception as e:
                logger.error(f"Error getting channel stats: {e}")
                return {}
    
    async def _estimate_search_volume(self, niche_name: str) -> int:
        """Estimate search volume based on niche name characteristics"""
        # Simple estimation based on niche characteristics
        base_volume = 50000  # Base monthly searches
        
        # Adjust based on niche characteristics
        common_words = ["how", "to", "tutorial", "review", "best", "vs"]
        if any(word in niche_name.lower() for word in common_words):
            base_volume *= 2
        
        # Adjust based on word count (shorter = more popular)
        word_count = len(niche_name.split())
        if word_count <= 2:
            base_volume *= 1.5
        elif word_count >= 4:
            base_volume *= 0.7
        
        return int(base_volume)
    
    def _calculate_estimated_cpm(self, categories: List[str], niche_name: str) -> float:
        """Calculate estimated CPM based on categories and niche"""
        if not categories:
            # Estimate based on niche name
            niche_lower = niche_name.lower()
            
            # High-value keywords
            if any(keyword in niche_lower for keyword in ["finance", "business", "investing", "money"]):
                return 12.0
            elif any(keyword in niche_lower for keyword in ["education", "tech", "science"]):
                return 4.5
            elif any(keyword in niche_lower for keyword in ["health", "fitness"]):
                return 3.5
            elif any(keyword in niche_lower for keyword in ["gaming", "entertainment"]):
                return 2.5
            else:
                return 3.0
        
        # Calculate based on actual categories
        cpm_values = []
        for category_id in categories:
            if category_id in self.category_cpm_estimates:
                cpm_values.append(self.category_cpm_estimates[category_id])
        
        return sum(cpm_values) / len(cpm_values) if cpm_values else 3.0
    
    def _calculate_channel_age_months(self, published_at: str) -> int:
        """Calculate channel age in months"""
        try:
            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now(published_date.tzinfo)
            delta = now - published_date
            return max(1, int(delta.days / 30))  # Convert to months
        except:
            return 12  # Default 1 year
    
    def _generate_estimated_metrics(self, niche_name: str, niche_id: int) -> List[Metric]:
        """Generate estimated metrics when API is unavailable"""
        metrics = []
        
        # Estimate search volume
        estimated_searches = self._estimate_search_volume(niche_name)
        metrics.append(Metric(
            niche_id=niche_id,
            metric_type="youtube_monthly_searches",
            value=estimated_searches,
            unit="count",
            confidence_score=40.0,
            collected_at=datetime.utcnow(),
            source_platform="youtube"
        ))
        
        # Estimate competition
        metrics.append(Metric(
            niche_id=niche_id,
            metric_type="channels_per_million_searches",
            value=150.0,  # Middle value
            unit="ratio",
            confidence_score=30.0,
            collected_at=datetime.utcnow(),
            source_platform="youtube"
        ))
        
        # Estimate growth rate
        metrics.append(Metric(
            niche_id=niche_id,
            metric_type="avg_monthly_subscriber_growth",
            value=15.0,  # Middle value
            unit="percentage",
            confidence_score=30.0,
            collected_at=datetime.utcnow(),
            source_platform="youtube"
        ))
        
        # Estimate CPM
        estimated_cpm = self._calculate_estimated_cpm([], niche_name)
        metrics.append(Metric(
            niche_id=niche_id,
            metric_type="estimated_cpm",
            value=estimated_cpm,
            unit="currency",
            confidence_score=40.0,
            collected_at=datetime.utcnow(),
            source_platform="youtube"
        ))
        
        return metrics

    async def discover_trending_niches(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Discover trending niches from YouTube data"""
        niches = []
        
        try:
            # Get trending videos
            trending_videos = await self._get_trending_videos(limit)
            
            # Extract potential niches from trending content
            niche_candidates = self._extract_niches_from_videos(trending_videos)
            
            for niche_data in niche_candidates:
                niches.append({
                    "name": niche_data["name"],
                    "source": "youtube_trending",
                    "confidence": niche_data["confidence"],
                    "keywords": niche_data["keywords"],
                    "estimated_volume": niche_data.get("estimated_volume", 0)
                })
        
        except Exception as e:
            logger.error(f"Error discovering trending niches: {e}")
        
        return niches
    
    async def _get_trending_videos(self, limit: int) -> List[Dict[str, Any]]:
        """Get trending videos from YouTube"""
        if not self.api_key:
            return []
        
        url = f"{self.base_api_url}/videos"
        params = {
            "part": "snippet,statistics",
            "chart": "mostPopular",
            "regionCode": "US",
            "maxResults": min(limit, 50),
            "key": self.api_key
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("items", [])
                    return []
            except Exception as e:
                logger.error(f"Error getting trending videos: {e}")
                return []
    
    def _extract_niches_from_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract potential niches from video data"""
        niches = []
        niche_counts = {}
        
        for video in videos:
            snippet = video.get("snippet", {})
            title = snippet.get("title", "").lower()
            description = snippet.get("description", "").lower()
            
            # Extract potential niche keywords
            keywords = self._extract_niche_keywords(title + " " + description)
            
            for keyword in keywords:
                if keyword not in niche_counts:
                    niche_counts[keyword] = {"count": 0, "videos": []}
                niche_counts[keyword]["count"] += 1
                niche_counts[keyword]["videos"].append(video.get("id"))
        
        # Convert to niche list
        for niche_name, data in niche_counts.items():
            if data["count"] >= 3:  # At least 3 videos mention this niche
                niches.append({
                    "name": niche_name,
                    "confidence": min(data["count"] * 10, 100),
                    "keywords": [niche_name],
                    "estimated_volume": data["count"] * 1000,
                    "sample_videos": data["videos"][:5]
                })
        
        return sorted(niches, key=lambda x: x["confidence"], reverse=True)
    
    def _extract_niche_keywords(self, text: str) -> List[str]:
        """Extract potential niche keywords from text"""
        # Simple keyword extraction - could be enhanced with NLP
        common_niches = [
            "gaming", "fitness", "cooking", "travel", "music", "comedy",
            "education", "tech", "fashion", "beauty", "health", "finance",
            "business", "investing", "cryptocurrency", "ai", "programming",
            "diy", "crafts", "art", "photography", "sports", "cars",
            "real estate", "productivity", "mindfulness", "relationships"
        ]
        
        found_keywords = []
        for niche in common_niches:
            if niche in text:
                found_keywords.append(niche)
        
        return found_keywords