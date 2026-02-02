"""
Niche Discovery Service - Main discovery engine
"""

import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from .scoring import NicheScorer, NicheMetrics
from .scrapers.youtube_scraper import YouTubeScraper
from .scrapers.trends_scraper import GoogleTrendsScraper
from .scrapers.reddit_scraper import RedditScraper
from .scrapers.tiktok_scraper import TikTokScraper

logger = logging.getLogger(__name__)

class NicheDiscoveryEngine:
    """Main niche discovery and validation engine"""
    
    def __init__(self):
        self.scorer = NicheScorer()
        self.youtube_scraper = YouTubeScraper()
        self.trends_scraper = GoogleTrendsScraper()
        self.reddit_scraper = RedditScraper()
        self.tiktok_scraper = TikTokScraper()
        
        # Discovery configuration
        self.discovery_sources = [
            "youtube_trending",
            "google_trends", 
            "reddit_growing_subs",
            "tiktok_hashtags",
            "news_topics"
        ]
        
        # Predefined seed niches for testing
        self.seed_niches = [
            # Tech & AI
            "AI tutorials", "ChatGPT guides", "coding tutorials", "tech reviews",
            "cryptocurrency news", "NFT explained", "blockchain basics",
            
            # Finance & Business  
            "personal finance", "stock market analysis", "real estate investing",
            "passive income", "side hustles", "business tips", "dropshipping",
            
            # Health & Fitness
            "workout routines", "healthy recipes", "weight loss", "mental health",
            "meditation guides", "yoga for beginners", "nutrition facts",
            
            # Lifestyle & Entertainment
            "morning routines", "productivity hacks", "life hacks", "travel vlogs",
            "fashion hauls", "cooking tutorials", "DIY projects",
            
            # Education & Development
            "language learning", "study techniques", "skill development",
            "career advice", "interview tips", "public speaking",
            
            # Gaming & Tech
            "gaming tutorials", "game reviews", "streaming setup",
            "tech unboxing", "smartphone reviews", "app recommendations",
            
            # Creative & Arts
            "digital art", "photography tips", "video editing", "music production",
            "drawing tutorials", "creative writing", "design tutorials"
        ]
    
    async def discover_niches(self, 
                            sources: Optional[List[str]] = None,
                            limit: int = 50,
                            min_score_threshold: float = 50.0) -> List[Dict[str, Any]]:
        """
        Main discovery method - finds and scores potential niches
        """
        logger.info(f"Starting niche discovery with {limit} target niches, min score {min_score_threshold}")
        
        sources = sources or self.discovery_sources
        discovered_niches = []
        
        try:
            # Discover potential niches from various sources
            potential_niches = await self._gather_potential_niches(sources)
            logger.info(f"Found {len(potential_niches)} potential niches")
            
            # Analyze and score each niche
            for niche_name in potential_niches[:limit * 2]:  # Analyze more than limit to filter
                try:
                    niche_data = await self._analyze_niche(niche_name)
                    if niche_data and niche_data['score']['total_score'] >= min_score_threshold:
                        discovered_niches.append(niche_data)
                        
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error analyzing niche '{niche_name}': {e}")
                    continue
            
            # Sort by score and return top results
            discovered_niches.sort(key=lambda x: x['score']['total_score'], reverse=True)
            return discovered_niches[:limit]
            
        except Exception as e:
            logger.error(f"Error in niche discovery: {e}")
            return []
    
    async def _gather_potential_niches(self, sources: List[str]) -> List[str]:
        """Gather potential niche names from various sources"""
        all_niches = set()
        
        for source in sources:
            try:
                if source == "youtube_trending":
                    niches = await self._get_youtube_trending_niches()
                elif source == "google_trends":
                    niches = await self._get_trending_topics()
                elif source == "reddit_growing_subs":
                    niches = await self._get_reddit_growing_topics()
                elif source == "tiktok_hashtags":
                    niches = await self._get_tiktok_trending()
                elif source == "news_topics":
                    niches = self._get_news_trending_topics()
                else:
                    niches = []
                
                all_niches.update(niches)
                logger.info(f"Source '{source}' provided {len(niches)} potential niches")
                
            except Exception as e:
                logger.error(f"Error gathering from source '{source}': {e}")
                continue
        
        # Add seed niches for testing
        all_niches.update(self.seed_niches)
        
        return list(all_niches)
    
    async def _analyze_niche(self, niche_name: str) -> Optional[Dict[str, Any]]:
        """Comprehensive analysis of a single niche"""
        try:
            logger.debug(f"Analyzing niche: {niche_name}")
            
            # Gather metrics from various sources concurrently
            tasks = [
                self._get_youtube_metrics(niche_name),
                self._get_trends_metrics(niche_name),
                self._get_reddit_metrics(niche_name),
                self._get_tiktok_metrics(niche_name)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine metrics
            metrics = NicheMetrics()
            
            # YouTube metrics
            if not isinstance(results[0], Exception) and results[0]:
                yt_data = results[0]
                metrics.search_volume = yt_data.get('search_volume', 0)
                metrics.channel_count = yt_data.get('channel_count', 0)
                metrics.avg_subscriber_growth = yt_data.get('avg_growth', 0.0)
                metrics.cpm_estimate = yt_data.get('estimated_cpm', 2.0)
                
            # Google Trends metrics  
            if not isinstance(results[1], Exception) and results[1]:
                trends_data = results[1]
                metrics.google_trends_score = trends_data.get('trend_score', 0)
                metrics.trend_growth_12m = trends_data.get('growth_12m', 0.0)
                
            # Reddit metrics
            if not isinstance(results[2], Exception) and results[2]:
                reddit_data = results[2]
                metrics.reddit_members = reddit_data.get('members', 0)
                
            # TikTok metrics
            if not isinstance(results[3], Exception) and results[3]:
                tiktok_data = results[3]
                metrics.tiktok_posts = tiktok_data.get('post_count', 0)
            
            # Estimate other metrics
            metrics.brand_safety_level = self._estimate_brand_safety(niche_name)
            metrics.news_coverage = self._estimate_news_coverage(niche_name)
            metrics.social_sentiment = self._estimate_sentiment(niche_name)
            
            # Calculate score
            score_result = self.scorer.calculate_total_score(metrics)
            
            return {
                "niche_name": niche_name,
                "score": score_result,
                "metrics": {
                    "search_volume": metrics.search_volume,
                    "google_trends_score": metrics.google_trends_score,
                    "channel_count": metrics.channel_count,
                    "avg_subscriber_growth": round(metrics.avg_subscriber_growth, 3),
                    "cpm_estimate": round(metrics.cpm_estimate, 2),
                    "brand_safety_level": metrics.brand_safety_level,
                    "reddit_members": metrics.reddit_members,
                    "tiktok_posts": metrics.tiktok_posts,
                    "news_coverage": metrics.news_coverage,
                    "trend_growth_12m": round(metrics.trend_growth_12m, 3),
                    "social_sentiment": round(metrics.social_sentiment, 3)
                },
                "analyzed_at": datetime.utcnow().isoformat(),
                "data_sources": ["youtube", "google_trends", "reddit", "tiktok"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing niche '{niche_name}': {e}")
            return None
    
    async def _get_youtube_trending_niches(self) -> List[str]:
        """Get trending topics from YouTube"""
        try:
            return await self.youtube_scraper.get_trending_topics()
        except:
            # Fallback to sample trending topics
            return ["AI automation", "ChatGPT tutorials", "productivity hacks", 
                   "side hustles 2024", "passive income", "crypto news"]
    
    async def _get_trending_topics(self) -> List[str]:
        """Get trending topics from Google Trends"""
        try:
            return await self.trends_scraper.get_trending_topics()
        except:
            return ["artificial intelligence", "remote work", "sustainable living"]
    
    async def _get_reddit_growing_topics(self) -> List[str]:
        """Get growing topics from Reddit"""
        try:
            return await self.reddit_scraper.get_growing_topics()
        except:
            return ["personal finance", "career advice", "mental health"]
    
    async def _get_tiktok_trending(self) -> List[str]:
        """Get trending hashtags from TikTok"""
        try:
            return await self.tiktok_scraper.get_trending_hashtags()
        except:
            return ["life hacks", "morning routine", "productivity"]
    
    def _get_news_trending_topics(self) -> List[str]:
        """Get trending topics from news sources"""
        # Placeholder - would integrate with news APIs
        return ["climate change", "electric vehicles", "space exploration", 
               "renewable energy", "digital privacy"]
    
    async def _get_youtube_metrics(self, niche: str) -> Dict[str, Any]:
        """Get YouTube-specific metrics for a niche"""
        try:
            return await self.youtube_scraper.get_niche_metrics(niche)
        except Exception as e:
            logger.warning(f"YouTube metrics failed for '{niche}': {e}")
            # Return estimated values
            return {
                'search_volume': random.randint(10000, 500000),
                'channel_count': random.randint(50, 1000),
                'avg_growth': random.uniform(0.05, 0.25),
                'estimated_cpm': random.uniform(1.0, 8.0)
            }
    
    async def _get_trends_metrics(self, niche: str) -> Dict[str, Any]:
        """Get Google Trends metrics"""
        try:
            return await self.trends_scraper.get_niche_metrics(niche)
        except Exception as e:
            logger.warning(f"Trends metrics failed for '{niche}': {e}")
            return {
                'trend_score': random.randint(30, 95),
                'growth_12m': random.uniform(-0.1, 0.8)
            }
    
    async def _get_reddit_metrics(self, niche: str) -> Dict[str, Any]:
        """Get Reddit metrics"""
        try:
            return await self.reddit_scraper.get_niche_metrics(niche)
        except Exception as e:
            logger.warning(f"Reddit metrics failed for '{niche}': {e}")
            return {
                'members': random.randint(1000, 200000)
            }
    
    async def _get_tiktok_metrics(self, niche: str) -> Dict[str, Any]:
        """Get TikTok metrics"""
        try:
            return await self.tiktok_scraper.get_niche_metrics(niche)
        except Exception as e:
            logger.warning(f"TikTok metrics failed for '{niche}': {e}")
            return {
                'post_count': random.randint(10000, 10000000)
            }
    
    def _estimate_brand_safety(self, niche: str) -> str:
        """Estimate brand safety level based on niche name"""
        risky_keywords = ['adult', 'controversial', 'politics', 'religion', 'gambling']
        mature_keywords = ['dating', 'relationship', 'alcohol', 'mature']
        
        niche_lower = niche.lower()
        
        if any(keyword in niche_lower for keyword in risky_keywords):
            return "controversial"
        elif any(keyword in niche_lower for keyword in mature_keywords):
            return "mature"
        elif any(word in niche_lower for word in ['family', 'kids', 'education', 'tutorial']):
            return "family"
        else:
            return "general"
    
    def _estimate_news_coverage(self, niche: str) -> str:
        """Estimate news coverage frequency"""
        high_coverage = ['ai', 'tech', 'crypto', 'politics', 'health', 'climate']
        medium_coverage = ['business', 'finance', 'education', 'science']
        
        niche_lower = niche.lower()
        
        if any(keyword in niche_lower for keyword in high_coverage):
            return "daily"
        elif any(keyword in niche_lower for keyword in medium_coverage):
            return "weekly"
        else:
            return "occasional"
    
    def _estimate_sentiment(self, niche: str) -> float:
        """Estimate social sentiment (0.0-1.0)"""
        positive_keywords = ['success', 'growth', 'tutorial', 'guide', 'tips', 'healthy']
        negative_keywords = ['problem', 'crisis', 'failure', 'scam', 'toxic']
        
        niche_lower = niche.lower()
        
        if any(keyword in niche_lower for keyword in positive_keywords):
            return random.uniform(0.7, 0.9)
        elif any(keyword in niche_lower for keyword in negative_keywords):
            return random.uniform(0.3, 0.5)
        else:
            return random.uniform(0.5, 0.7)

# Example usage
async def test_discovery():
    """Test the discovery engine"""
    engine = NicheDiscoveryEngine()
    
    print("🔍 Testing Niche Discovery Engine...")
    
    # Discover top niches
    niches = await engine.discover_niches(limit=10, min_score_threshold=60.0)
    
    print(f"\n📊 Discovered {len(niches)} high-scoring niches:")
    
    for i, niche in enumerate(niches[:5], 1):
        print(f"\n{i}. {niche['niche_name']}")
        print(f"   Score: {niche['score']['total_score']}/100 ({niche['score']['grade']})")
        print(f"   {niche['score']['recommendation']}")
        print(f"   Search Volume: {niche['metrics']['search_volume']:,}")
        print(f"   CPM Estimate: ${niche['metrics']['cpm_estimate']}")

if __name__ == "__main__":
    asyncio.run(test_discovery())