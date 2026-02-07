"""
Scoring Service - 100-Point Niche Scoring Algorithm
Based on PM Agent specifications for YouTube Niche Discovery Engine
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.niche import Niche
from app.models.metric import Metric
from app.models.trend import Trend
from app.core.config import settings
from app.services.cpm_estimator import get_cpm_estimator, CPMEstimator

logger = logging.getLogger(__name__)

class ScoringService:
    """
    100-Point Niche Scoring Algorithm Implementation - PM Agent Specification
    
    EXACT BREAKDOWN (PM_DELIVERABLES.md):
    1. Search Volume (25 points)
       - Google Trends Score (0-100): 15 points
       - YouTube Search Volume (Monthly): 10 points
    2. Competition Level (25 points - inverse scoring)
       - Channel Saturation Analysis: 15 points
       - Subscriber Growth Rate: 10 points
    3. Monetization Potential (20 points)
       - CPM Rate Tier: 15 points
       - Brand Safety Score: 5 points
    4. Content Availability (15 points)
       - Reddit Activity Score: 5 points
       - TikTok Content Volume: 5 points
       - News/Blog Coverage: 5 points
    5. Trend Momentum (15 points)
       - 12-Month Trend Analysis: 10 points
       - Social Media Momentum: 5 points
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        # Initialize the CPM estimator (uses comprehensive database with 70+ categories)
        self.cpm_estimator = get_cpm_estimator()
        
        # CPM tiers for scoring (points based on CPM value)
        # Uses real CPM data from the estimator instead of hardcoded values
        self.cpm_tiers = {
            "tier_1": {"min_cpm": 10.0, "points": 15},  # Ultra-premium: Finance, Insurance, B2B
            "tier_2": {"min_cpm": 6.0, "points": 12},   # Premium: Real Estate, Legal, VPN
            "tier_3": {"min_cpm": 4.0, "points": 9},    # Moderate-high: Education, Tech, Health
            "tier_4": {"min_cpm": 2.0, "points": 6},    # Moderate: Lifestyle, Cooking, Fitness
            "tier_5": {"min_cpm": 0.0, "points": 3},    # Entertainment: Gaming, Comedy, Music
        }
    
    async def calculate_niche_score(self, niche_id: int) -> Dict[str, float]:
        """
        Calculate 100-point niche score using PM Agent's exact algorithm
        
        Returns:
            Dict with individual scores and overall score (0-100)
        """
        try:
            # Get niche data
            niche = await self._get_niche(niche_id)
            if not niche:
                logger.error(f"Niche {niche_id} not found")
                return self._default_scores()
            
            # Get recent metrics for the niche
            recent_metrics = await self._get_recent_metrics(niche_id)
            
            if not recent_metrics:
                logger.warning(f"No metrics found for niche {niche_id}, using defaults")
                return self._default_scores()
            
            # Calculate individual component scores using PM algorithm
            search_volume_score = await self._calculate_search_volume_score_pm(recent_metrics)
            competition_score = await self._calculate_competition_score_pm(recent_metrics)
            monetization_score = await self._calculate_monetization_score_pm(niche, recent_metrics)
            content_availability_score = await self._calculate_content_availability_score_pm(recent_metrics)
            trend_momentum_score = await self._calculate_trend_momentum_score_pm(niche_id, recent_metrics)
            
            # Calculate overall score (PM weights)
            overall_score = (
                search_volume_score +           # 25 points max
                competition_score +             # 25 points max  
                monetization_score +            # 20 points max
                content_availability_score +    # 15 points max
                trend_momentum_score            # 15 points max
            )
            
            scores = {
                "overall_score": round(min(100, max(0, overall_score)), 2),
                "search_volume_score": round(search_volume_score, 2),
                "competition_score": round(competition_score, 2),
                "monetization_score": round(monetization_score, 2),
                "content_availability_score": round(content_availability_score, 2),
                "trend_momentum_score": round(trend_momentum_score, 2),
                # For compatibility with existing model
                "trend_score": round(trend_momentum_score, 2),
                "audience_score": round((search_volume_score + content_availability_score) / 2, 2),
                "content_opportunity_score": round(content_availability_score, 2)
            }
            
            logger.info(f"PM Algorithm scores for niche {niche.name}: {overall_score:.1f}/100 "
                       f"[SV:{search_volume_score:.1f}, C:{competition_score:.1f}, "
                       f"M:{monetization_score:.1f}, CA:{content_availability_score:.1f}, "
                       f"TM:{trend_momentum_score:.1f}]")
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating score for niche {niche_id}: {e}")
            return self._default_scores()
    
    async def _calculate_search_volume_score_pm(self, recent_metrics: List[Metric]) -> float:
        """
        1. SEARCH VOLUME (25 Points) - PM Agent Specification
        
        - Google Trends Score (0-100): 15 points
          * 90-100 = 15 points
          * 70-89 = 12 points  
          * 50-69 = 9 points
          * 30-49 = 6 points
          * <30 = 3 points
        
        - YouTube Search Volume (Monthly): 10 points
          * 1M+ = 10 points
          * 500K-1M = 8 points
          * 100K-500K = 6 points
          * 50K-100K = 4 points
          * <50K = 2 points
        """
        try:
            google_trends_score = 0.0
            youtube_search_score = 0.0
            
            # Google Trends Score (15 points max)
            trends_metrics = [m for m in recent_metrics if m.metric_type == "google_trends_score"]
            if trends_metrics:
                trends_value = trends_metrics[0].value
                if trends_value >= 90:
                    google_trends_score = 15.0
                elif trends_value >= 70:
                    google_trends_score = 12.0
                elif trends_value >= 50:
                    google_trends_score = 9.0
                elif trends_value >= 30:
                    google_trends_score = 6.0
                else:
                    google_trends_score = 3.0
            else:
                # Default middle score if no data
                google_trends_score = 6.0
            
            # YouTube Search Volume (10 points max)
            yt_search_metrics = [m for m in recent_metrics if m.metric_type == "youtube_monthly_searches"]
            if yt_search_metrics:
                yt_searches = yt_search_metrics[0].value
                if yt_searches >= 1_000_000:
                    youtube_search_score = 10.0
                elif yt_searches >= 500_000:
                    youtube_search_score = 8.0
                elif yt_searches >= 100_000:
                    youtube_search_score = 6.0
                elif yt_searches >= 50_000:
                    youtube_search_score = 4.0
                else:
                    youtube_search_score = 2.0
            else:
                # Default middle score if no data
                youtube_search_score = 4.0
            
            total_score = google_trends_score + youtube_search_score
            logger.debug(f"Search volume score: Google Trends {google_trends_score}/15, YouTube {youtube_search_score}/10, Total: {total_score}/25")
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating search volume score: {e}")
            return 10.0  # Default middle score
    
    async def _calculate_competition_score_pm(self, recent_metrics: List[Metric]) -> float:
        """
        2. COMPETITION LEVEL (25 Points - Inverse Scoring) - PM Agent Specification
        
        - Channel Saturation Analysis: 15 points
          * <50 channels per 1M searches = 15 points
          * 50-100 channels = 12 points
          * 100-200 channels = 9 points
          * 200-500 channels = 6 points
          * 500+ channels = 3 points
        
        - Subscriber Growth Rate: 10 points
          * <5% monthly growth = 10 points
          * 5-10% growth = 8 points
          * 10-20% growth = 6 points
          * 20-30% growth = 4 points
          * >30% growth = 2 points
        """
        try:
            channel_saturation_score = 0.0
            subscriber_growth_score = 0.0
            
            # Channel Saturation Analysis (15 points max)
            saturation_metrics = [m for m in recent_metrics if m.metric_type == "channels_per_million_searches"]
            if saturation_metrics:
                channels_per_mil = saturation_metrics[0].value
                if channels_per_mil < 50:
                    channel_saturation_score = 15.0
                elif channels_per_mil < 100:
                    channel_saturation_score = 12.0
                elif channels_per_mil < 200:
                    channel_saturation_score = 9.0
                elif channels_per_mil < 500:
                    channel_saturation_score = 6.0
                else:
                    channel_saturation_score = 3.0
            else:
                # Default middle score if no data
                channel_saturation_score = 9.0
            
            # Subscriber Growth Rate (10 points max)
            growth_metrics = [m for m in recent_metrics if m.metric_type == "avg_monthly_subscriber_growth"]
            if growth_metrics:
                growth_rate = growth_metrics[0].value
                if growth_rate < 5:
                    subscriber_growth_score = 10.0
                elif growth_rate < 10:
                    subscriber_growth_score = 8.0
                elif growth_rate < 20:
                    subscriber_growth_score = 6.0
                elif growth_rate < 30:
                    subscriber_growth_score = 4.0
                else:
                    subscriber_growth_score = 2.0
            else:
                # Default middle score if no data
                subscriber_growth_score = 6.0
            
            total_score = channel_saturation_score + subscriber_growth_score
            logger.debug(f"Competition score: Channel saturation {channel_saturation_score}/15, Growth rate {subscriber_growth_score}/10, Total: {total_score}/25")
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating competition score: {e}")
            return 15.0  # Default middle score
    
    async def _calculate_monetization_score_pm(self, niche: Niche, recent_metrics: List[Metric]) -> float:
        """
        3. MONETIZATION POTENTIAL (20 Points) - PM Agent Specification
        
        - CPM Rate Tier: 15 points
          * $10+ CPM = 15 points (Finance, Insurance, B2B)
          * $6-10 CPM = 12 points (Real Estate, Legal, VPN)
          * $4-6 CPM = 9 points (Education, Tech, Health)
          * $2-4 CPM = 6 points (Lifestyle, Gaming, Cooking)
          * <$2 CPM = 3 points (Comedy, Music, Kids)
        
        - Brand Safety Score: 5 points
          * Family-friendly content = 5 points
          * General audience = 4 points
          * Mature (non-explicit) = 3 points
          * Controversial = 2 points
          * Adult/explicit = 1 point
        
        Uses the comprehensive CPM database (70+ categories) with fuzzy matching.
        Sources: Lenostube, Outlierkit, FirstGrowthAgency, SMBillion
        """
        try:
            cpm_score = 0.0
            brand_safety_score = 0.0
            
            # CPM Rate Tier (15 points max)
            cpm_metrics = [m for m in recent_metrics if m.metric_type == "estimated_cpm"]
            
            if cpm_metrics:
                cpm_value = cpm_metrics[0].value
            else:
                # Use the comprehensive CPM estimator for intelligent matching
                niche_name = niche.name if niche.name else ""
                niche_category = niche.category if niche.category else None
                
                # Get CPM estimate from the database (no geographic/seasonal adjustment for scoring)
                cpm_result = self.cpm_estimator.estimate_cpm(
                    niche_name=niche_name,
                    niche_category=niche_category,
                    apply_seasonal=False,
                    apply_geographic=False,
                )
                cpm_value = cpm_result.get("base_cpm", cpm_result.get("cpm", 3.5))
                
                # Log the match for debugging
                logger.debug(f"CPM estimate for '{niche_name}': ${cpm_value:.2f} "
                           f"(match: {cpm_result.get('match_type', 'unknown')}, "
                           f"confidence: {cpm_result.get('confidence', 0):.0%})")
            
            # Calculate points from CPM value
            if cpm_value >= 10.0:
                cpm_score = 15.0
            elif cpm_value >= 6.0:
                cpm_score = 12.0
            elif cpm_value >= 4.0:
                cpm_score = 9.0
            elif cpm_value >= 2.0:
                cpm_score = 6.0
            else:
                cpm_score = 3.0
            
            # Brand Safety Score (5 points max)
            brand_safety_metrics = [m for m in recent_metrics if m.metric_type == "brand_safety_score"]
            if brand_safety_metrics:
                brand_safety_value = brand_safety_metrics[0].value
                brand_safety_score = min(brand_safety_value, 5.0)
            else:
                # Estimate based on niche category
                niche_category = niche.category.lower() if niche.category else ""
                niche_name_lower = niche.name.lower() if niche.name else ""
                combined = f"{niche_name_lower} {niche_category}"
                
                # Family-friendly indicators
                if any(kw in combined for kw in ["education", "finance", "health", "family", "tutorial", "learning"]):
                    brand_safety_score = 5.0
                # General audience
                elif any(kw in combined for kw in ["tech", "business", "lifestyle", "cooking", "travel", "fitness"]):
                    brand_safety_score = 4.0
                # Mature but safe
                elif any(kw in combined for kw in ["gaming", "entertainment", "anime", "manga", "comedy"]):
                    brand_safety_score = 3.5
                # Potentially controversial
                elif any(kw in combined for kw in ["politics", "news", "crypto", "controversy"]):
                    brand_safety_score = 2.5
                else:
                    brand_safety_score = 4.0  # Default general audience
            
            total_score = cpm_score + brand_safety_score
            logger.debug(f"Monetization score: CPM {cpm_score}/15 (${cpm_value:.2f}), "
                        f"Brand safety {brand_safety_score}/5, Total: {total_score}/20")
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating monetization score: {e}")
            return 12.0  # Default middle score
    
    async def _calculate_content_availability_score_pm(self, recent_metrics: List[Metric]) -> float:
        """
        4. CONTENT AVAILABILITY (15 Points) - PM Agent Specification
        
        - Reddit Activity Score: 5 points
          * 100K+ members = 5 points
          * 50K-100K = 4 points
          * 10K-50K = 3 points
          * 1K-10K = 2 points
          * <1K = 1 point
        
        - TikTok Content Volume: 5 points
          * >10M posts = 5 points
          * 1-10M = 4 points
          * 100K-1M = 3 points
          * 10K-100K = 2 points
          * <10K = 1 point
        
        - News/Blog Coverage: 5 points
          * Daily coverage = 5 points
          * Weekly = 4 points
          * Monthly = 3 points
          * Occasional = 2 points
          * Rare = 1 point
        """
        try:
            reddit_score = 0.0
            tiktok_score = 0.0
            news_score = 0.0
            
            # Reddit Activity Score (5 points max)
            reddit_metrics = [m for m in recent_metrics if m.metric_type == "reddit_subreddit_members"]
            if reddit_metrics:
                reddit_members = reddit_metrics[0].value
                if reddit_members >= 100_000:
                    reddit_score = 5.0
                elif reddit_members >= 50_000:
                    reddit_score = 4.0
                elif reddit_members >= 10_000:
                    reddit_score = 3.0
                elif reddit_members >= 1_000:
                    reddit_score = 2.0
                else:
                    reddit_score = 1.0
            else:
                reddit_score = 2.5  # Default middle
            
            # TikTok Content Volume (5 points max)
            tiktok_metrics = [m for m in recent_metrics if m.metric_type == "tiktok_hashtag_posts"]
            if tiktok_metrics:
                tiktok_posts = tiktok_metrics[0].value
                if tiktok_posts >= 10_000_000:
                    tiktok_score = 5.0
                elif tiktok_posts >= 1_000_000:
                    tiktok_score = 4.0
                elif tiktok_posts >= 100_000:
                    tiktok_score = 3.0
                elif tiktok_posts >= 10_000:
                    tiktok_score = 2.0
                else:
                    tiktok_score = 1.0
            else:
                tiktok_score = 2.5  # Default middle
            
            # News/Blog Coverage (5 points max)
            news_metrics = [m for m in recent_metrics if m.metric_type == "news_coverage_frequency"]
            if news_metrics:
                news_frequency = news_metrics[0].value  # Assume 1-5 scale
                news_score = min(news_frequency, 5.0)
            else:
                news_score = 2.5  # Default middle
            
            total_score = reddit_score + tiktok_score + news_score
            logger.debug(f"Content availability score: Reddit {reddit_score}/5, TikTok {tiktok_score}/5, News {news_score}/5, Total: {total_score}/15")
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating content availability score: {e}")
            return 7.5  # Default middle score
    
    async def _calculate_trend_momentum_score_pm(self, niche_id: int, recent_metrics: List[Metric]) -> float:
        """
        5. TREND MOMENTUM (15 Points) - PM Agent Specification
        
        - 12-Month Trend Analysis: 10 points
          * 50%+ YoY growth = 10 points
          * 20-50% growth = 8 points
          * 0-20% growth = 6 points
          * 0 to -20% decline = 4 points
          * >20% decline = 2 points
        
        - Social Media Momentum: 5 points
          * Cross-platform growth, viral frequency, influencer adoption
          
        Direction-aware scoring:
        - Rising trends get bonus points
        - Falling trends get penalty
        - Goal: 80→40 should score LOWER than 40→80
        """
        try:
            trend_analysis_score = 0.0
            social_momentum_score = 0.0
            direction_adjustment = 0.0
            
            # Check for trend_direction metric (from Google Trends direction detection)
            direction_metrics = [m for m in recent_metrics 
                               if m.metric_name == "trend_direction" and m.metric_type == "trend_momentum"]
            
            trend_direction = 'stable'
            direction_confidence = 50.0
            period_change = 0.0
            
            if direction_metrics:
                dm = direction_metrics[0]
                # Decode direction from value: 1=rising, 0=stable, -1=falling
                if dm.value > 0:
                    trend_direction = 'rising'
                elif dm.value < 0:
                    trend_direction = 'falling'
                
                direction_confidence = dm.confidence_score or 50.0
                
                # Try to get more details from raw_data
                if dm.raw_data:
                    try:
                        raw = json.loads(dm.raw_data) if isinstance(dm.raw_data, str) else dm.raw_data
                        trend_direction = raw.get('direction', trend_direction)
                        period_change = raw.get('period_change', 0.0)
                    except (json.JSONDecodeError, TypeError):
                        pass
            
            # 12-Month Trend Analysis (10 points max)
            trend_metrics = [m for m in recent_metrics if m.metric_type == "yearly_growth_rate"]
            
            if trend_metrics:
                yoy_growth = trend_metrics[0].value
            elif period_change != 0:
                # Use period change from direction detection as proxy for growth
                yoy_growth = period_change
            else:
                # Get historical data to calculate trend
                yoy_growth = None
                historical_trends = await self._get_historical_trends(niche_id, days_back=365)
                if len(historical_trends) >= 2:
                    recent_score = historical_trends[0].overall_score
                    old_score = historical_trends[-1].overall_score
                    if old_score > 0:
                        yoy_growth = ((recent_score - old_score) / old_score) * 100
            
            if yoy_growth is not None:
                if yoy_growth >= 50:
                    trend_analysis_score = 10.0
                elif yoy_growth >= 20:
                    trend_analysis_score = 8.0
                elif yoy_growth >= 0:
                    trend_analysis_score = 6.0
                elif yoy_growth >= -20:
                    trend_analysis_score = 4.0
                else:
                    trend_analysis_score = 2.0
            else:
                trend_analysis_score = 6.0  # Default neutral
            
            # Apply direction adjustment (critical for 80→40 vs 40→80 differentiation)
            # Rising trends get up to +2 bonus points
            # Falling trends get up to -2 penalty points
            confidence_factor = min(direction_confidence / 100, 1.0)
            
            if trend_direction == 'rising':
                direction_adjustment = 2.0 * confidence_factor
                logger.debug(f"Rising trend detected, adding {direction_adjustment:.1f} bonus points")
            elif trend_direction == 'falling':
                direction_adjustment = -2.0 * confidence_factor
                logger.debug(f"Falling trend detected, applying {direction_adjustment:.1f} penalty points")
            
            # Social Media Momentum (5 points max)
            social_metrics = [m for m in recent_metrics if m.metric_type in [
                "social_momentum_score", "viral_content_frequency", "influencer_adoption_rate"
            ]]
            if social_metrics:
                momentum_scores = [m.value for m in social_metrics]
                avg_momentum = sum(momentum_scores) / len(momentum_scores)
                social_momentum_score = min(avg_momentum / 20, 5.0)
            else:
                social_momentum_score = 2.5  # Default middle
            
            # Calculate total with direction adjustment, clamped to valid range
            base_total = trend_analysis_score + social_momentum_score
            total_score = max(0, min(15, base_total + direction_adjustment))
            
            logger.debug(f"Trend momentum score: 12-month {trend_analysis_score}/10, "
                        f"Social {social_momentum_score}/5, Direction adj: {direction_adjustment:+.1f}, "
                        f"Total: {total_score:.1f}/15 (dir: {trend_direction})")
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating trend momentum score: {e}")
            return 8.0  # Default middle score
    
    async def _get_niche(self, niche_id: int) -> Optional[Niche]:
        """Get niche by ID"""
        query = select(Niche).where(Niche.id == niche_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_recent_metrics(self, niche_id: int, days_back: int = 7) -> List[Metric]:
        """Get recent metrics for a niche"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(Metric).where(
            and_(
                Metric.niche_id == niche_id,
                Metric.collected_at >= cutoff_date
            )
        ).order_by(Metric.collected_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def _get_historical_trends(self, niche_id: int, days_back: int = 365) -> List[Trend]:
        """Get historical trend data for momentum calculation"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(Trend).where(
            and_(
                Trend.niche_id == niche_id,
                Trend.timestamp >= cutoff_date
            )
        ).order_by(Trend.timestamp.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_niche_scores(self, niche_id: int) -> bool:
        """Update scores for a specific niche"""
        try:
            # Calculate new scores
            scores = await self.calculate_niche_score(niche_id)
            
            # Get the niche
            niche = await self._get_niche(niche_id)
            if not niche:
                logger.error(f"Niche {niche_id} not found")
                return False
            
            # Update scores
            niche.overall_score = scores["overall_score"]
            niche.trend_score = scores["trend_score"]
            niche.competition_score = scores["competition_score"]
            niche.monetization_score = scores["monetization_score"]
            niche.audience_score = scores["audience_score"]
            niche.content_opportunity_score = scores["content_opportunity_score"]
            
            await self.session.commit()
            
            # Create trend entry for historical tracking
            await self._create_trend_entry(niche, scores)
            
            logger.info(f"Updated scores for niche {niche.name}: {scores['overall_score']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating scores for niche {niche_id}: {e}")
            await self.session.rollback()
            return False
    
    async def batch_update_scores(self, limit: Optional[int] = None) -> int:
        """Update scores for all active niches"""
        query = select(Niche).where(Niche.is_active == True)
        if limit:
            query = query.limit(limit)
        
        result = await self.session.execute(query)
        niches = result.scalars().all()
        
        updated_count = 0
        for niche in niches:
            if await self.update_niche_scores(niche.id):
                updated_count += 1
        
        logger.info(f"Updated scores for {updated_count} niches")
        return updated_count
    
    async def _create_trend_entry(self, niche: Niche, scores: Dict[str, float]):
        """Create a trend entry for historical tracking"""
        try:
            # Get the last trend entry for comparison
            last_trend_query = select(Trend).where(
                Trend.niche_id == niche.id
            ).order_by(Trend.timestamp.desc()).limit(1)
            
            result = await self.session.execute(last_trend_query)
            last_trend = result.scalar_one_or_none()
            
            # Calculate score change
            score_change = 0.0
            if last_trend:
                score_change = scores["overall_score"] - last_trend.overall_score
            
            # Determine trend direction
            trend_direction = "stable"
            if score_change > 2:
                trend_direction = "up"
            elif score_change < -2:
                trend_direction = "down"
            
            # Create new trend entry
            trend = Trend(
                niche_id=niche.id,
                timestamp=datetime.utcnow(),
                period_type="daily",
                overall_score=scores["overall_score"],
                trend_score=scores["trend_score"],
                competition_score=scores["competition_score"],
                monetization_score=scores["monetization_score"],
                audience_score=scores["audience_score"],
                content_opportunity_score=scores["content_opportunity_score"],
                score_change=score_change,
                trend_direction=trend_direction,
                momentum=abs(score_change),
                confidence_level=95.0  # Default confidence
            )
            
            self.session.add(trend)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Error creating trend entry: {e}")
    
    def _default_scores(self) -> Dict[str, float]:
        """Return default scores when calculation fails"""
        return {
            "overall_score": 50.0,
            "search_volume_score": 10.0,
            "competition_score": 15.0,
            "monetization_score": 12.0,
            "content_availability_score": 7.5,
            "trend_momentum_score": 8.0,
            # For compatibility
            "trend_score": 8.0,
            "audience_score": 8.75,
            "content_opportunity_score": 7.5
        }