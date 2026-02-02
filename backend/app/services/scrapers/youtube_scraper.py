"""
YouTube Data Scraper - Search volume, channel analysis, trending topics
"""

import asyncio
import logging
import random
import aiohttp
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class YouTubeScraper:
    """YouTube data scraper for niche analysis"""
    
    def __init__(self):
        self.session = None
        # CPM estimates by category (from PM research)
        self.cpm_estimates = {
            'finance': 12.0, 'business': 8.0, 'education': 4.9, 'tech': 4.15,
            'lifestyle': 3.73, 'health': 3.60, 'beauty': 3.00, 'gaming': 3.11,
            'entertainment': 2.98, 'cooking': 2.50, 'travel': 2.00, 'fitness': 1.60,
            'comedy': 1.00, 'music': 1.50, 'diy': 2.50, 'tutorial': 4.0,
            'ai': 8.0, 'crypto': 10.0, 'investing': 12.0
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics/niches from YouTube"""
        # Simulated trending topics - in production would use YouTube API
        trending_topics = [
            "AI automation tools",
            "passive income 2024", 
            "productivity morning routine",
            "cryptocurrency explained",
            "remote work setup",
            "healthy meal prep",
            "side hustle ideas",
            "digital marketing tips",
            "coding for beginners",
            "personal finance basics",
            "travel photography",
            "meditation for anxiety",
            "sustainable living",
            "workout from home",
            "language learning apps"
        ]
        
        # Randomize and return subset
        random.shuffle(trending_topics)
        return trending_topics[:10]
    
    async def get_niche_metrics(self, niche_name: str) -> Dict[str, Any]:
        """Get comprehensive YouTube metrics for a niche"""
        try:
            logger.debug(f"Getting YouTube metrics for: {niche_name}")
            
            # Simulate API calls with realistic data
            search_volume = self._estimate_search_volume(niche_name)
            channel_count = self._estimate_channel_count(niche_name, search_volume)
            avg_growth = self._estimate_growth_rate(niche_name)
            estimated_cpm = self._estimate_cpm(niche_name)
            
            # Add some realistic variance
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            return {
                'search_volume': search_volume,
                'channel_count': channel_count,
                'avg_growth': avg_growth,
                'estimated_cpm': estimated_cpm,
                'competition_level': self._calculate_competition(channel_count, search_volume),
                'trending_score': random.randint(60, 95)
            }
            
        except Exception as e:
            logger.error(f"Error getting YouTube metrics for '{niche_name}': {e}")
            raise
    
    def _estimate_search_volume(self, niche: str) -> int:
        """Estimate monthly search volume based on niche characteristics"""
        base_volume = 50000
        
        # High-volume keywords
        high_volume_keywords = [
            'ai', 'crypto', 'bitcoin', 'money', 'tutorial', 'guide', 'tips',
            'workout', 'diet', 'recipe', 'travel', 'productivity', 'motivation'
        ]
        
        # Medium-volume keywords  
        medium_volume_keywords = [
            'business', 'marketing', 'coding', 'learning', 'health', 'fitness',
            'beauty', 'fashion', 'lifestyle', 'gaming', 'tech', 'review'
        ]
        
        niche_lower = niche.lower()
        
        # Calculate multiplier based on keywords
        multiplier = 1.0
        
        for keyword in high_volume_keywords:
            if keyword in niche_lower:
                multiplier *= random.uniform(3.0, 8.0)
                break
        
        for keyword in medium_volume_keywords:
            if keyword in niche_lower:
                multiplier *= random.uniform(1.5, 3.0)
                break
        
        # Add length penalty (longer niches tend to have lower volume)
        length_penalty = max(0.3, 1.0 - (len(niche.split()) * 0.1))
        multiplier *= length_penalty
        
        volume = int(base_volume * multiplier)
        
        # Realistic bounds
        return max(5000, min(2000000, volume))
    
    def _estimate_channel_count(self, niche: str, search_volume: int) -> int:
        """Estimate number of channels in this niche"""
        # Competition ratio: channels per 100k searches
        base_ratio = random.uniform(5, 50)  # 5-50 channels per 100k searches
        
        # Adjust based on niche characteristics
        competitive_keywords = ['money', 'finance', 'crypto', 'business', 'marketing']
        if any(keyword in niche.lower() for keyword in competitive_keywords):
            base_ratio *= random.uniform(1.5, 3.0)  # More competition
        
        channel_count = int((search_volume / 100000) * base_ratio)
        
        return max(10, min(5000, channel_count))
    
    def _estimate_growth_rate(self, niche: str) -> float:
        """Estimate average subscriber growth rate for channels in this niche"""
        base_growth = 0.15  # 15% monthly growth
        
        # Hot niches grow faster
        trending_keywords = ['ai', 'crypto', 'nft', '2024', 'new', 'trending']
        if any(keyword in niche.lower() for keyword in trending_keywords):
            base_growth *= random.uniform(1.2, 2.0)
        
        # Saturated niches grow slower
        saturated_keywords = ['gaming', 'music', 'comedy', 'entertainment']
        if any(keyword in niche.lower() for keyword in saturated_keywords):
            base_growth *= random.uniform(0.5, 0.8)
        
        return round(random.uniform(base_growth * 0.7, base_growth * 1.3), 3)
    
    def _estimate_cpm(self, niche: str) -> float:
        """Estimate CPM based on niche category"""
        niche_lower = niche.lower()
        
        # Check for specific keywords and assign CPM
        for category, cpm in self.cpm_estimates.items():
            if category in niche_lower:
                # Add variance
                variance = cpm * 0.3  # ±30% variance
                return round(random.uniform(cpm - variance, cpm + variance), 2)
        
        # Default CPM for unrecognized niches
        return round(random.uniform(2.0, 4.0), 2)
    
    def _calculate_competition(self, channel_count: int, search_volume: int) -> str:
        """Calculate competition level"""
        ratio = (channel_count / search_volume) * 100000
        
        if ratio < 10:
            return "LOW"
        elif ratio < 25:
            return "MEDIUM"
        elif ratio < 50:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    async def get_channel_analysis(self, niche: str, limit: int = 20) -> Dict[str, Any]:
        """Analyze top channels in a niche"""
        # Placeholder for detailed channel analysis
        return {
            'top_channels': [],
            'average_subscribers': random.randint(10000, 500000),
            'average_views': random.randint(5000, 100000),
            'growth_trend': random.choice(['rising', 'stable', 'declining']),
            'content_frequency': random.uniform(1.0, 7.0)  # videos per week
        }
    
    async def search_suggestions(self, query: str) -> List[str]:
        """Get YouTube search suggestions for a query"""
        # Simulate search suggestions
        base_suggestions = [
            f"{query} tutorial",
            f"{query} guide", 
            f"{query} tips",
            f"{query} for beginners",
            f"{query} 2024",
            f"best {query}",
            f"how to {query}",
            f"{query} explained",
            f"{query} review",
            f"{query} vs"
        ]
        
        return base_suggestions[:random.randint(5, 8)]

# Example usage
async def test_youtube_scraper():
    """Test the YouTube scraper"""
    scraper = YouTubeScraper()
    
    print("🎥 Testing YouTube Scraper...")
    
    # Test trending topics
    trending = await scraper.get_trending_topics()
    print(f"\n📈 Trending Topics: {trending[:3]}")
    
    # Test niche analysis
    test_niche = "AI tutorials"
    metrics = await scraper.get_niche_metrics(test_niche)
    print(f"\n📊 Metrics for '{test_niche}':")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(test_youtube_scraper())