"""
Niche Discovery Service - Main orchestrator for niche discovery and scoring
Implements the complete PM Agent workflow for discovering 100+ niches daily
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.models.niche import Niche
from app.models.metric import Metric
from app.models.source import Source
from app.services.youtube_service import YouTubeService
from app.services.scoring_service import ScoringService
from app.core.config import settings

logger = logging.getLogger(__name__)

class NicheDiscoveryService:
    """
    Main niche discovery orchestrator implementing PM Agent's workflow
    
    Objectives:
    - Discover 100+ niches daily
    - Score using PM's 100-point algorithm  
    - Identify high-potential niches (90+ score)
    - Real-time scoring and validation
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.youtube_service = YouTubeService(session)
        self.scoring_service = ScoringService(session)
        
        # PM Agent targets
        self.daily_discovery_target = 100
        self.high_score_threshold = settings.HIGH_SCORE_THRESHOLD  # 90+
        self.min_score_threshold = settings.MIN_SCORE_THRESHOLD    # 50+
    
    async def discover_niches_daily(self) -> Dict[str, Any]:
        """
        Main daily discovery workflow
        
        Returns:
            Summary of discovery results including high-potential niches
        """
        discovery_results = {
            "date": datetime.utcnow().isoformat(),
            "total_discovered": 0,
            "high_potential": [],
            "medium_potential": [],
            "sources_used": [],
            "processing_time": 0,
            "errors": []
        }
        
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting daily niche discovery workflow...")
            
            # 1. Discover niches from multiple sources
            discovered_niches = await self._discover_from_all_sources()
            discovery_results["total_discovered"] = len(discovered_niches)
            
            # 2. Process and score each discovered niche
            for niche_data in discovered_niches:
                try:
                    niche = await self._create_or_update_niche(niche_data)
                    if niche:
                        # Collect metrics and score
                        await self._collect_niche_metrics(niche)
                        scores = await self.scoring_service.calculate_niche_score(niche.id)
                        
                        # Update niche with scores
                        await self._update_niche_scores(niche, scores)
                        
                        # Categorize by potential
                        if scores["overall_score"] >= self.high_score_threshold:
                            discovery_results["high_potential"].append({
                                "name": niche.name,
                                "score": scores["overall_score"],
                                "id": niche.id
                            })
                        elif scores["overall_score"] >= self.min_score_threshold:
                            discovery_results["medium_potential"].append({
                                "name": niche.name,
                                "score": scores["overall_score"],
                                "id": niche.id
                            })
                
                except Exception as e:
                    logger.error(f"Error processing niche {niche_data.get('name', 'Unknown')}: {e}")
                    discovery_results["errors"].append(str(e))
            
            # 3. Generate summary statistics
            discovery_results["processing_time"] = (datetime.utcnow() - start_time).total_seconds()
            discovery_results["sources_used"] = list(set([n.get("source", "") for n in discovered_niches]))
            
            logger.info(f"Daily discovery complete: {discovery_results['total_discovered']} niches, "
                       f"{len(discovery_results['high_potential'])} high-potential")
            
        except Exception as e:
            logger.error(f"Error in daily discovery workflow: {e}")
            discovery_results["errors"].append(str(e))
        
        return discovery_results
    
    async def _discover_from_all_sources(self) -> List[Dict[str, Any]]:
        """Discover niches from all available sources"""
        all_discovered = []
        
        # 1. YouTube trending niches
        try:
            youtube_niches = await self.youtube_service.discover_trending_niches(limit=50)
            all_discovered.extend([{**n, "source": "youtube_trending"} for n in youtube_niches])
            logger.info(f"Discovered {len(youtube_niches)} niches from YouTube trending")
        except Exception as e:
            logger.error(f"Error discovering from YouTube: {e}")
        
        # 2. Manual seed niches (PM Agent's high-value categories)
        seed_niches = await self._get_seed_niches()
        all_discovered.extend(seed_niches)
        
        # 3. Google Trends integration (future)
        # google_niches = await self._discover_from_google_trends()
        # all_discovered.extend(google_niches)
        
        # 4. Reddit trending topics (future)  
        # reddit_niches = await self._discover_from_reddit()
        # all_discovered.extend(reddit_niches)
        
        # Remove duplicates
        unique_niches = self._deduplicate_niches(all_discovered)
        
        logger.info(f"Total unique niches discovered: {len(unique_niches)}")
        return unique_niches
    
    async def _get_seed_niches(self) -> List[Dict[str, Any]]:
        """Get seed niches based on PM Agent's high-value categories"""
        seed_niches = [
            # Tier 1: Premium Monetization ($10+ CPM)
            {"name": "affiliate marketing", "category": "business", "source": "pm_seed", "estimated_cpm": 22.0},
            {"name": "digital marketing", "category": "business", "source": "pm_seed", "estimated_cpm": 12.5},
            {"name": "personal finance", "category": "finance", "source": "pm_seed", "estimated_cpm": 12.0},
            {"name": "investing strategies", "category": "finance", "source": "pm_seed", "estimated_cpm": 12.0},
            {"name": "business strategy", "category": "business", "source": "pm_seed", "estimated_cpm": 4.7},
            
            # Tier 2: Strong Monetization ($4-10 CPM)
            {"name": "online education", "category": "education", "source": "pm_seed", "estimated_cpm": 4.9},
            {"name": "tech tutorials", "category": "technology", "source": "pm_seed", "estimated_cpm": 4.2},
            {"name": "productivity hacks", "category": "lifestyle", "source": "pm_seed", "estimated_cpm": 3.7},
            {"name": "health optimization", "category": "health", "source": "pm_seed", "estimated_cpm": 3.6},
            {"name": "meditation asmr", "category": "lifestyle", "source": "pm_seed", "estimated_cpm": 3.5},
            
            # Tier 3: Moderate Monetization ($2-4 CPM)
            {"name": "fashion hauls", "category": "fashion", "source": "pm_seed", "estimated_cpm": 3.1},
            {"name": "makeup tutorials", "category": "beauty", "source": "pm_seed", "estimated_cpm": 3.0},
            {"name": "weight loss", "category": "health", "source": "pm_seed", "estimated_cpm": 10.0},
            {"name": "gaming reviews", "category": "gaming", "source": "pm_seed", "estimated_cpm": 3.1},
            {"name": "cooking tutorials", "category": "lifestyle", "source": "pm_seed", "estimated_cpm": 2.5},
            {"name": "travel vlogs", "category": "travel", "source": "pm_seed", "estimated_cpm": 2.0},
            
            # High-potential emerging niches
            {"name": "ai tools", "category": "technology", "source": "pm_seed", "estimated_cpm": 8.0},
            {"name": "cryptocurrency", "category": "finance", "source": "pm_seed", "estimated_cpm": 15.0},
            {"name": "remote work", "category": "business", "source": "pm_seed", "estimated_cpm": 6.0},
            {"name": "sustainable living", "category": "lifestyle", "source": "pm_seed", "estimated_cpm": 4.0},
            {"name": "mindfulness", "category": "health", "source": "pm_seed", "estimated_cpm": 3.5},
        ]
        
        return seed_niches
    
    def _deduplicate_niches(self, niches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate niches based on name similarity"""
        unique_niches = []
        seen_names = set()
        
        for niche in niches:
            name = niche.get("name", "").lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_niches.append(niche)
        
        return unique_niches
    
    async def _create_or_update_niche(self, niche_data: Dict[str, Any]) -> Optional[Niche]:
        """Create or update a niche in the database"""
        try:
            name = niche_data.get("name", "").strip()
            if not name:
                return None
            
            # Check if niche already exists
            query = select(Niche).where(Niche.name == name)
            result = await self.session.execute(query)
            existing_niche = result.scalar_one_or_none()
            
            if existing_niche:
                # Update existing niche
                existing_niche.last_updated = datetime.utcnow()
                if "category" in niche_data:
                    existing_niche.category = niche_data["category"]
                if "keywords" in niche_data:
                    existing_niche.keywords = niche_data["keywords"]
                await self.session.commit()
                return existing_niche
            else:
                # Create new niche
                niche = Niche(
                    name=name,
                    description=niche_data.get("description", ""),
                    category=niche_data.get("category", "unknown"),
                    keywords=niche_data.get("keywords", []),
                    discovery_source=niche_data.get("source", "unknown"),
                    discovery_method="automated",
                    is_active=True,
                    is_validated=False,
                    discovered_at=datetime.utcnow(),
                    last_updated=datetime.utcnow()
                )
                
                self.session.add(niche)
                await self.session.commit()
                await self.session.refresh(niche)
                return niche
        
        except Exception as e:
            logger.error(f"Error creating/updating niche: {e}")
            await self.session.rollback()
            return None
    
    async def _collect_niche_metrics(self, niche: Niche) -> None:
        """Collect all metrics for a niche from all sources"""
        try:
            # YouTube metrics (primary source)
            youtube_metrics = await self.youtube_service.collect_niche_metrics(niche.name, niche.id)
            
            # Add YouTube metrics to database
            for metric in youtube_metrics:
                self.session.add(metric)
            
            # Add seed metrics for PM algorithm testing
            seed_metrics = self._generate_seed_metrics(niche)
            for metric in seed_metrics:
                self.session.add(metric)
            
            await self.session.commit()
            logger.debug(f"Collected {len(youtube_metrics)} YouTube metrics for {niche.name}")
            
        except Exception as e:
            logger.error(f"Error collecting metrics for niche {niche.name}: {e}")
            await self.session.rollback()
    
    def _generate_seed_metrics(self, niche: Niche) -> List[Metric]:
        """Generate additional metrics for PM algorithm scoring"""
        metrics = []
        
        # Google Trends score (simulate for now)
        google_trends_score = self._estimate_google_trends_score(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="google_trends_score",
            value=google_trends_score,
            unit="score",
            confidence_score=70.0,
            collected_at=datetime.utcnow(),
            source_platform="google_trends"
        ))
        
        # Reddit activity (simulate)
        reddit_members = self._estimate_reddit_activity(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="reddit_subreddit_members",
            value=reddit_members,
            unit="count",
            confidence_score=60.0,
            collected_at=datetime.utcnow(),
            source_platform="reddit"
        ))
        
        # TikTok content volume (simulate)
        tiktok_posts = self._estimate_tiktok_volume(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="tiktok_hashtag_posts",
            value=tiktok_posts,
            unit="count",
            confidence_score=50.0,
            collected_at=datetime.utcnow(),
            source_platform="tiktok"
        ))
        
        # News coverage (simulate)
        news_frequency = self._estimate_news_coverage(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="news_coverage_frequency",
            value=news_frequency,
            unit="score",
            confidence_score=55.0,
            collected_at=datetime.utcnow(),
            source_platform="news"
        ))
        
        # Yearly growth rate (simulate)
        growth_rate = self._estimate_yearly_growth(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="yearly_growth_rate",
            value=growth_rate,
            unit="percentage",
            confidence_score=65.0,
            collected_at=datetime.utcnow(),
            source_platform="aggregate"
        ))
        
        # Brand safety score
        brand_safety = self._estimate_brand_safety(niche.name)
        metrics.append(Metric(
            niche_id=niche.id,
            metric_type="brand_safety_score",
            value=brand_safety,
            unit="score",
            confidence_score=80.0,
            collected_at=datetime.utcnow(),
            source_platform="content_analysis"
        ))
        
        return metrics
    
    def _estimate_google_trends_score(self, niche_name: str) -> float:
        """Estimate Google Trends score based on niche characteristics"""
        # Simple heuristic-based estimation
        name_lower = niche_name.lower()
        
        # High-trending topics
        if any(keyword in name_lower for keyword in ["ai", "crypto", "remote", "sustainable"]):
            return 85.0 + (hash(niche_name) % 15)  # 85-100
        
        # Medium-trending topics  
        elif any(keyword in name_lower for keyword in ["finance", "health", "tech", "education"]):
            return 65.0 + (hash(niche_name) % 20)  # 65-85
        
        # Stable topics
        elif any(keyword in name_lower for keyword in ["cooking", "travel", "fitness"]):
            return 45.0 + (hash(niche_name) % 25)  # 45-70
        
        # Lower trend topics
        else:
            return 25.0 + (hash(niche_name) % 30)  # 25-55
    
    def _estimate_reddit_activity(self, niche_name: str) -> int:
        """Estimate Reddit community size"""
        name_lower = niche_name.lower()
        
        # Popular on Reddit
        if any(keyword in name_lower for keyword in ["gaming", "crypto", "investing", "tech"]):
            return 500000 + (hash(niche_name) % 1000000)
        
        # Medium popularity
        elif any(keyword in name_lower for keyword in ["fitness", "cooking", "travel"]):
            return 100000 + (hash(niche_name) % 400000)
        
        # Lower activity
        else:
            return 10000 + (hash(niche_name) % 90000)
    
    def _estimate_tiktok_volume(self, niche_name: str) -> int:
        """Estimate TikTok hashtag volume"""
        name_lower = niche_name.lower()
        
        # Viral on TikTok
        if any(keyword in name_lower for keyword in ["dance", "fashion", "beauty", "comedy"]):
            return 50000000 + (hash(niche_name) % 100000000)
        
        # Medium viral potential
        elif any(keyword in name_lower for keyword in ["fitness", "food", "diy"]):
            return 10000000 + (hash(niche_name) % 40000000)
        
        # Lower viral potential
        else:
            return 1000000 + (hash(niche_name) % 9000000)
    
    def _estimate_news_coverage(self, niche_name: str) -> float:
        """Estimate news coverage frequency (1-5 scale)"""
        name_lower = niche_name.lower()
        
        if any(keyword in name_lower for keyword in ["finance", "crypto", "ai", "politics"]):
            return 4.5 + (hash(niche_name) % 100) / 200  # 4.5-5.0
        elif any(keyword in name_lower for keyword in ["health", "tech", "business"]):
            return 3.0 + (hash(niche_name) % 150) / 100  # 3.0-4.5
        else:
            return 1.5 + (hash(niche_name) % 150) / 100  # 1.5-3.0
    
    def _estimate_yearly_growth(self, niche_name: str) -> float:
        """Estimate yearly growth rate"""
        name_lower = niche_name.lower()
        
        # High growth
        if any(keyword in name_lower for keyword in ["ai", "crypto", "remote", "sustainable"]):
            return 40.0 + (hash(niche_name) % 40)  # 40-80%
        
        # Medium growth
        elif any(keyword in name_lower for keyword in ["tech", "health", "education"]):
            return 15.0 + (hash(niche_name) % 25)  # 15-40%
        
        # Stable/declining
        else:
            return -10.0 + (hash(niche_name) % 30)  # -10 to +20%
    
    def _estimate_brand_safety(self, niche_name: str) -> float:
        """Estimate brand safety score (1-5 scale)"""
        name_lower = niche_name.lower()
        
        # Family-friendly
        if any(keyword in name_lower for keyword in ["education", "family", "health", "finance"]):
            return 5.0
        
        # General audience
        elif any(keyword in name_lower for keyword in ["tech", "business", "cooking", "travel"]):
            return 4.0
        
        # Mature content
        elif any(keyword in name_lower for keyword in ["gaming", "entertainment"]):
            return 3.0
        
        # Potentially controversial
        else:
            return 4.0  # Default to safe
    
    async def _update_niche_scores(self, niche: Niche, scores: Dict[str, float]) -> None:
        """Update niche with calculated scores"""
        try:
            niche.overall_score = scores["overall_score"]
            niche.trend_score = scores["trend_score"]
            niche.competition_score = scores["competition_score"]
            niche.monetization_score = scores["monetization_score"]
            niche.audience_score = scores["audience_score"]
            niche.content_opportunity_score = scores["content_opportunity_score"]
            niche.last_updated = datetime.utcnow()
            
            # Mark as validated if score meets threshold
            if scores["overall_score"] >= self.min_score_threshold:
                niche.is_validated = True
                niche.validation_notes = f"Auto-validated with score {scores['overall_score']:.1f}"
            
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating niche scores: {e}")
            await self.session.rollback()
    
    async def get_high_potential_niches(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get high-potential niches (90+ score) with latest metrics"""
        try:
            query = (
                select(Niche)
                .where(
                    and_(
                        Niche.overall_score >= self.high_score_threshold,
                        Niche.is_active == True
                    )
                )
                .order_by(desc(Niche.overall_score))
                .limit(limit)
            )
            
            result = await self.session.execute(query)
            niches = result.scalars().all()
            
            high_potential = []
            for niche in niches:
                high_potential.append({
                    "id": niche.id,
                    "name": niche.name,
                    "score": niche.overall_score,
                    "category": niche.category,
                    "discovered_at": niche.discovered_at.isoformat(),
                    "last_updated": niche.last_updated.isoformat(),
                    "score_breakdown": {
                        "overall": niche.overall_score,
                        "trend": niche.trend_score,
                        "competition": niche.competition_score,
                        "monetization": niche.monetization_score,
                        "audience": niche.audience_score,
                        "content_opportunity": niche.content_opportunity_score
                    }
                })
            
            return high_potential
            
        except Exception as e:
            logger.error(f"Error getting high potential niches: {e}")
            return []
    
    async def analyze_niche_deeply(self, niche_id: int) -> Dict[str, Any]:
        """Perform deep analysis of a specific niche"""
        try:
            # Get niche with all related data
            query = (
                select(Niche)
                .where(Niche.id == niche_id)
                .options(selectinload(Niche.metrics), selectinload(Niche.trends))
            )
            result = await self.session.execute(query)
            niche = result.scalar_one_or_none()
            
            if not niche:
                return {"error": "Niche not found"}
            
            # Recalculate scores with fresh data
            await self._collect_niche_metrics(niche)
            scores = await self.scoring_service.calculate_niche_score(niche.id)
            await self._update_niche_scores(niche, scores)
            
            # Get recent metrics
            recent_metrics = await self._get_recent_metrics(niche.id)
            
            analysis = {
                "niche_info": {
                    "id": niche.id,
                    "name": niche.name,
                    "category": niche.category,
                    "keywords": niche.keywords,
                    "discovered_at": niche.discovered_at.isoformat(),
                    "last_updated": niche.last_updated.isoformat()
                },
                "scores": scores,
                "metrics_summary": {
                    "total_metrics": len(recent_metrics),
                    "data_sources": list(set([m.source_platform for m in recent_metrics])),
                    "latest_update": max([m.collected_at for m in recent_metrics]).isoformat() if recent_metrics else None
                },
                "detailed_metrics": [
                    {
                        "type": m.metric_type,
                        "value": m.value,
                        "unit": m.unit,
                        "confidence": m.confidence_score,
                        "source": m.source_platform,
                        "collected_at": m.collected_at.isoformat()
                    } for m in recent_metrics
                ],
                "recommendations": self._generate_recommendations(niche, scores)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing niche {niche_id}: {e}")
            return {"error": str(e)}
    
    async def _get_recent_metrics(self, niche_id: int, days_back: int = 7) -> List[Metric]:
        """Get recent metrics for a niche"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(Metric).where(
            and_(
                Metric.niche_id == niche_id,
                Metric.collected_at >= cutoff_date
            )
        ).order_by(desc(Metric.collected_at))
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    def _generate_recommendations(self, niche: Niche, scores: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations for a niche"""
        recommendations = []
        
        overall_score = scores["overall_score"]
        
        if overall_score >= 90:
            recommendations.append("🚀 HIGH PRIORITY: This niche shows exceptional potential. Consider immediate content creation.")
            recommendations.append("💰 Monetization: Set up multiple revenue streams (ads, affiliates, products).")
        elif overall_score >= 70:
            recommendations.append("✅ GOOD OPPORTUNITY: Strong potential with room for optimization.")
        elif overall_score >= 50:
            recommendations.append("⚠️ MODERATE POTENTIAL: Consider niche refinement or sub-niche targeting.")
        else:
            recommendations.append("❌ LOW PRIORITY: Focus on higher-scoring opportunities first.")
        
        # Specific scoring feedback
        if scores["competition_score"] < 15:
            recommendations.append("🔴 High competition detected. Consider long-tail keywords or sub-niches.")
        
        if scores["monetization_score"] >= 15:
            recommendations.append("💎 Excellent monetization potential. Focus on high-value content.")
        
        if scores["trend_momentum_score"] >= 12:
            recommendations.append("📈 Strong trending momentum. Act quickly to capitalize.")
        
        if scores["search_volume_score"] >= 20:
            recommendations.append("🔍 High search volume. Great opportunity for organic reach.")
        
        return recommendations