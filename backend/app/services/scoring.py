"""
Niche Scoring Algorithm - 100 Point System
Based on PM Agent specifications
"""

import math
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class NicheMetrics:
    """Data structure for niche metrics"""
    search_volume: int = 0
    google_trends_score: int = 0
    channel_count: int = 0
    avg_subscriber_growth: float = 0.0
    cpm_estimate: float = 0.0
    brand_safety_level: str = "family"  # family, general, mature, controversial, adult
    reddit_members: int = 0
    tiktok_posts: int = 0
    news_coverage: str = "occasional"  # daily, weekly, monthly, occasional, rare
    trend_growth_12m: float = 0.0
    social_sentiment: float = 0.5  # 0.0-1.0

class NicheScorer:
    """Implementation of the 100-point niche scoring algorithm"""
    
    def __init__(self):
        self.max_score = 100
        
    def calculate_total_score(self, metrics: NicheMetrics) -> Dict[str, Any]:
        """Calculate the complete 100-point score breakdown"""
        
        # Component scores
        search_volume_score = self._calculate_search_volume_score(metrics)
        competition_score = self._calculate_competition_score(metrics)
        monetization_score = self._calculate_monetization_score(metrics)
        content_availability_score = self._calculate_content_availability_score(metrics)
        trend_momentum_score = self._calculate_trend_momentum_score(metrics)
        
        # Total score
        total_score = (
            search_volume_score + 
            competition_score + 
            monetization_score + 
            content_availability_score + 
            trend_momentum_score
        )
        
        # Determine grade
        grade = self._get_grade(total_score)
        
        return {
            "total_score": round(total_score, 1),
            "grade": grade,
            "breakdown": {
                "search_volume": {
                    "score": round(search_volume_score, 1),
                    "max": 25,
                    "percentage": round((search_volume_score / 25) * 100, 1)
                },
                "competition": {
                    "score": round(competition_score, 1),
                    "max": 25,
                    "percentage": round((competition_score / 25) * 100, 1)
                },
                "monetization": {
                    "score": round(monetization_score, 1),
                    "max": 20,
                    "percentage": round((monetization_score / 20) * 100, 1)
                },
                "content_availability": {
                    "score": round(content_availability_score, 1),
                    "max": 15,
                    "percentage": round((content_availability_score / 15) * 100, 1)
                },
                "trend_momentum": {
                    "score": round(trend_momentum_score, 1),
                    "max": 15,
                    "percentage": round((trend_momentum_score / 15) * 100, 1)
                }
            },
            "recommendation": self._get_recommendation(total_score),
            "risk_level": self._get_risk_level(total_score)
        }
    
    def _calculate_search_volume_score(self, metrics: NicheMetrics) -> float:
        """Search Volume: 25 points max"""
        score = 0.0
        
        # Google Trends Score (0-100): 15 points max
        trends_score = metrics.google_trends_score
        if trends_score >= 90:
            score += 15
        elif trends_score >= 70:
            score += 12
        elif trends_score >= 50:
            score += 9
        elif trends_score >= 30:
            score += 6
        else:
            score += 3
        
        # YouTube Search Volume (Monthly): 10 points max
        search_vol = metrics.search_volume
        if search_vol >= 1_000_000:
            score += 10
        elif search_vol >= 500_000:
            score += 8
        elif search_vol >= 100_000:
            score += 6
        elif search_vol >= 50_000:
            score += 4
        else:
            score += 2
            
        return score
    
    def _calculate_competition_score(self, metrics: NicheMetrics) -> float:
        """Competition Level: 25 points max (inverse scoring - less competition = more points)"""
        score = 0.0
        
        # Channel Saturation Analysis: 15 points max
        if metrics.search_volume > 0:
            channels_per_million = (metrics.channel_count / metrics.search_volume) * 1_000_000
        else:
            channels_per_million = metrics.channel_count
            
        if channels_per_million < 50:
            score += 15
        elif channels_per_million < 100:
            score += 12
        elif channels_per_million < 200:
            score += 9
        elif channels_per_million < 500:
            score += 6
        else:
            score += 3
        
        # Subscriber Growth Rate: 10 points max (lower growth = less competition)
        growth_rate = metrics.avg_subscriber_growth
        if growth_rate < 0.05:  # <5%
            score += 10
        elif growth_rate < 0.10:  # 5-10%
            score += 8
        elif growth_rate < 0.20:  # 10-20%
            score += 6
        elif growth_rate < 0.30:  # 20-30%
            score += 4
        else:  # >30%
            score += 2
            
        return score
    
    def _calculate_monetization_score(self, metrics: NicheMetrics) -> float:
        """Monetization Potential: 20 points max"""
        score = 0.0
        
        # CPM Rate Tier: 15 points max
        cpm = metrics.cpm_estimate
        if cpm >= 10:
            score += 15  # Premium (Finance, Business)
        elif cpm >= 4:
            score += 12  # Strong (Education, Tech)
        elif cpm >= 2:
            score += 9   # Moderate (Lifestyle, Beauty)
        elif cpm >= 1:
            score += 6   # Scale-based (Gaming, Fitness)
        else:
            score += 3   # Low (Comedy, Music)
        
        # Brand Safety Score: 5 points max
        brand_safety = metrics.brand_safety_level.lower()
        if brand_safety == "family":
            score += 5
        elif brand_safety == "general":
            score += 4
        elif brand_safety == "mature":
            score += 3
        elif brand_safety == "controversial":
            score += 2
        else:  # adult
            score += 1
            
        return score
    
    def _calculate_content_availability_score(self, metrics: NicheMetrics) -> float:
        """Content Availability: 15 points max"""
        score = 0.0
        
        # Reddit Activity Score: 5 points max
        reddit_members = metrics.reddit_members
        if reddit_members >= 100_000:
            score += 5
        elif reddit_members >= 50_000:
            score += 4
        elif reddit_members >= 10_000:
            score += 3
        elif reddit_members >= 1_000:
            score += 2
        else:
            score += 1
        
        # TikTok Content Volume: 5 points max
        tiktok_posts = metrics.tiktok_posts
        if tiktok_posts >= 10_000_000:
            score += 5
        elif tiktok_posts >= 1_000_000:
            score += 4
        elif tiktok_posts >= 100_000:
            score += 3
        elif tiktok_posts >= 10_000:
            score += 2
        else:
            score += 1
        
        # News/Blog Coverage: 5 points max
        news_coverage = metrics.news_coverage.lower()
        if news_coverage == "daily":
            score += 5
        elif news_coverage == "weekly":
            score += 4
        elif news_coverage == "monthly":
            score += 3
        elif news_coverage == "occasional":
            score += 2
        else:  # rare
            score += 1
            
        return score
    
    def _calculate_trend_momentum_score(self, metrics: NicheMetrics) -> float:
        """Trend Momentum: 15 points max"""
        score = 0.0
        
        # 12-Month Trend Analysis: 10 points max
        growth = metrics.trend_growth_12m
        if growth >= 0.5:  # 50%+ growth
            score += 10
        elif growth >= 0.2:  # 20-50% growth
            score += 8
        elif growth >= 0.0:  # 0-20% growth
            score += 6
        elif growth >= -0.2:  # 0 to -20% decline
            score += 4
        else:  # >20% decline
            score += 2
        
        # Social Sentiment Score: 5 points max
        sentiment = metrics.social_sentiment
        score += sentiment * 5  # 0.0-1.0 mapped to 0-5 points
        
        return score
    
    def _get_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 85:
            return "A+"  # Goldmine
        elif score >= 80:
            return "A"   # Excellent
        elif score >= 75:
            return "A-"  # Very Good
        elif score >= 70:
            return "B+"  # Good
        elif score >= 65:
            return "B"   # Decent
        elif score >= 60:
            return "B-"  # Marginal
        elif score >= 55:
            return "C+"  # Risky
        elif score >= 50:
            return "C"   # Poor
        else:
            return "F"   # Avoid
    
    def _get_recommendation(self, score: float) -> str:
        """Get actionable recommendation based on score"""
        if score >= 85:
            return "🔥 GOLDMINE: Immediate action recommended! High profit potential with manageable risk."
        elif score >= 75:
            return "✅ EXCELLENT: Strong opportunity. Invest resources for development."
        elif score >= 65:
            return "👍 GOOD: Solid potential. Consider for content calendar."
        elif score >= 55:
            return "⚠️ MARGINAL: Proceed with caution. Test with small investment first."
        elif score >= 45:
            return "❌ RISKY: High competition or low monetization. Not recommended."
        else:
            return "🚫 AVOID: Poor metrics across multiple categories."
    
    def _get_risk_level(self, score: float) -> str:
        """Determine risk level"""
        if score >= 75:
            return "LOW"
        elif score >= 60:
            return "MEDIUM"
        elif score >= 45:
            return "HIGH"
        else:
            return "VERY_HIGH"

# Example usage and testing
def test_scoring_algorithm():
    """Test the scoring algorithm with sample data"""
    scorer = NicheScorer()
    
    # Test case: High-scoring niche (AI tutorials)
    ai_metrics = NicheMetrics(
        search_volume=800_000,
        google_trends_score=85,
        channel_count=150,
        avg_subscriber_growth=0.15,
        cpm_estimate=8.50,
        brand_safety_level="family",
        reddit_members=250_000,
        tiktok_posts=5_000_000,
        news_coverage="weekly",
        trend_growth_12m=0.65,
        social_sentiment=0.8
    )
    
    result = scorer.calculate_total_score(ai_metrics)
    print("AI Tutorials Niche Score:")
    print(f"Total Score: {result['total_score']}/100 (Grade: {result['grade']})")
    print(f"Recommendation: {result['recommendation']}")
    
    return result

if __name__ == "__main__":
    test_scoring_algorithm()