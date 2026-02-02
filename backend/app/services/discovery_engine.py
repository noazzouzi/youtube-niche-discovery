"""
Niche Discovery Engine - Main orchestration service
Implements complete niche discovery workflow using PM Agent's 100-point algorithm
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from .youtube_service import YouTubeService
from .google_trends_service import GoogleTrendsService
from .reddit_service import RedditService
from .scoring_service import ScoringService
from app.models.niche import Niche
from app.models.metric import Metric
from app.models.source import Source
from app.core.database import get_session

logger = logging.getLogger(__name__)

class NicheDiscoveryEngine:
    """
    Complete niche discovery and validation system
    
    Implements PM Agent's workflow:
    1. Discover potential niches from multiple sources
    2. Collect comprehensive metrics for 100-point scoring
    3. Calculate scores using PM algorithm
    4. Rank and filter high-potential niches (80+ score)
    5. Provide actionable insights and recommendations
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
        # Initialize all data collection services
        self.youtube_service = YouTubeService(session)
        self.google_trends_service = GoogleTrendsService()
        self.reddit_service = RedditService()
        self.scoring_service = ScoringService(session)
        
        # Discovery configuration
        self.discovery_config = {
            "min_score_threshold": 70,     # Minimum score to consider viable
            "high_potential_threshold": 80, # High-potential alert threshold
            "discovery_batch_size": 50,    # Max niches to discover per run
            "metric_collection_timeout": 300,  # 5 minutes max per niche
            "concurrent_collections": 3    # Max parallel metric collection
        }
    
    async def discover_and_analyze_niches(self, 
                                        sources: List[str] = None, 
                                        limit: int = 50) -> Dict[str, Any]:
        """
        Main discovery workflow - find and analyze new niches
        
        Args:
            sources: List of sources to search ['youtube', 'google_trends', 'reddit']
            limit: Maximum number of new niches to discover
            
        Returns:
            Discovery report with high-scoring niches and insights
        """
        discovery_report = {
            "discovery_time": datetime.utcnow().isoformat(),
            "sources_used": sources or ["youtube", "google_trends", "reddit"],
            "niches_discovered": 0,
            "niches_analyzed": 0,
            "high_potential_niches": [],
            "processing_stats": {},
            "errors": []
        }
        
        try:
            logger.info("Starting niche discovery and analysis workflow")
            
            # 1. Discover potential niches from all sources
            potential_niches = await self._discover_from_sources(sources or ["youtube", "google_trends", "reddit"], limit)
            discovery_report["niches_discovered"] = len(potential_niches)
            
            if not potential_niches:
                logger.warning("No potential niches discovered")
                return discovery_report
            
            # 2. Filter out already analyzed niches
            new_niches = await self._filter_new_niches(potential_niches)
            
            # 3. Create niche entries in database
            created_niches = await self._create_niche_entries(new_niches)
            
            # 4. Collect metrics and analyze in batches
            analysis_results = await self._analyze_niches_batch(created_niches)
            discovery_report["niches_analyzed"] = len(analysis_results)
            discovery_report["processing_stats"] = analysis_results.get("stats", {})
            
            # 5. Identify high-potential niches
            high_potential = await self._identify_high_potential_niches()
            discovery_report["high_potential_niches"] = high_potential
            
            # 6. Generate insights and recommendations
            discovery_report["insights"] = await self._generate_discovery_insights(analysis_results)
            
            logger.info(f"Discovery completed: {discovery_report['niches_analyzed']} analyzed, {len(high_potential)} high-potential found")
            
        except Exception as e:
            logger.error(f"Error in discovery workflow: {e}")
            discovery_report["errors"].append(str(e))
        
        return discovery_report
    
    async def analyze_single_niche(self, niche_name: str, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze a single niche with complete metrics collection
        
        Args:
            niche_name: Name of the niche to analyze
            keywords: Additional keywords related to the niche
            
        Returns:
            Complete analysis report with scores and recommendations
        """
        analysis_report = {
            "niche_name": niche_name,
            "analysis_time": datetime.utcnow().isoformat(),
            "metrics_collected": {},
            "scores": {},
            "grade": "F",
            "recommendations": [],
            "market_insights": {},
            "errors": []
        }
        
        try:
            logger.info(f"Starting analysis for niche: {niche_name}")
            
            # 1. Create or get niche entry
            niche = await self._create_or_get_niche(niche_name, keywords or [])
            
            # 2. Collect comprehensive metrics
            metrics_result = await self._collect_all_metrics(niche.id, niche_name, keywords or [])
            analysis_report["metrics_collected"] = metrics_result["summary"]
            
            if metrics_result["errors"]:
                analysis_report["errors"].extend(metrics_result["errors"])
            
            # 3. Calculate scores using PM algorithm
            scores = await self.scoring_service.calculate_niche_score(niche.id)
            analysis_report["scores"] = scores
            
            # 4. Update niche with scores
            await self.scoring_service.update_niche_scores(niche.id)
            
            # 5. Get detailed score breakdown
            score_breakdown = await self.scoring_service.get_niche_score_breakdown(niche.id)
            analysis_report["grade"] = score_breakdown["grade"]
            analysis_report["recommendations"] = score_breakdown["recommendations"]
            
            # 6. Generate market insights
            analysis_report["market_insights"] = await self._generate_market_insights(niche.id, niche_name)
            
            logger.info(f"Analysis completed for '{niche_name}': Score {scores['overall_score']:.1f}/100 (Grade: {score_breakdown['grade']})")
            
        except Exception as e:
            logger.error(f"Error analyzing niche '{niche_name}': {e}")
            analysis_report["errors"].append(str(e))
        
        return analysis_report
    
    async def _discover_from_sources(self, sources: List[str], limit: int) -> List[Dict[str, Any]]:
        """Discover potential niches from multiple sources"""
        all_niches = []
        
        # Distribute limit across sources
        limit_per_source = max(limit // len(sources), 10)
        
        for source in sources:
            try:
                if source == "youtube":
                    niches = await self.youtube_service.get_trending_niches(limit_per_source)
                elif source == "google_trends":
                    niches = await self.google_trends_service.discover_trending_keywords()
                elif source == "reddit":
                    niches = await self.reddit_service.discover_trending_communities(limit_per_source)
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue
                
                # Add source information
                for niche in niches:
                    niche["discovery_source"] = source
                
                all_niches.extend(niches)
                logger.info(f"Discovered {len(niches)} potential niches from {source}")
                
            except Exception as e:
                logger.error(f"Error discovering from {source}: {e}")
        
        # Remove duplicates and sort by initial scores
        unique_niches = self._deduplicate_niches(all_niches)
        return unique_niches[:limit]
    
    async def _filter_new_niches(self, potential_niches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out niches that have already been analyzed recently"""
        new_niches = []
        cutoff_date = datetime.utcnow() - timedelta(days=7)  # Re-analyze after 7 days
        
        for niche_data in potential_niches:
            niche_name = niche_data.get("name", "").lower()
            
            # Check if niche exists and was analyzed recently
            query = select(Niche).where(
                and_(
                    Niche.name.ilike(f"%{niche_name}%"),
                    Niche.last_analyzed >= cutoff_date
                )
            )
            
            result = await self.session.execute(query)
            existing = result.scalar_one_or_none()
            
            if not existing:
                new_niches.append(niche_data)
        
        logger.info(f"Filtered to {len(new_niches)} new niches (out of {len(potential_niches)} discovered)")
        return new_niches
    
    async def _create_niche_entries(self, niche_data_list: List[Dict[str, Any]]) -> List[Niche]:
        """Create niche database entries"""
        created_niches = []
        
        for niche_data in niche_data_list:
            try:
                niche = Niche(
                    name=niche_data.get("name", ""),
                    description=niche_data.get("description", ""),
                    category=niche_data.get("category", "General"),
                    keywords=niche_data.get("keywords", []),
                    discovery_source=niche_data.get("discovery_source", "unknown"),
                    is_active=True,
                    is_validated=False,
                    discovered_at=datetime.utcnow(),
                    last_analyzed=datetime.utcnow()
                )
                
                self.session.add(niche)
                await self.session.flush()  # Get the ID
                created_niches.append(niche)
                
            except Exception as e:
                logger.error(f"Error creating niche entry: {e}")
        
        await self.session.commit()
        logger.info(f"Created {len(created_niches)} niche entries")
        return created_niches
    
    async def _analyze_niches_batch(self, niches: List[Niche]) -> Dict[str, Any]:
        """Analyze multiple niches in parallel batches"""
        analysis_stats = {
            "total_processed": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "avg_processing_time": 0,
            "metrics_collected": 0
        }
        
        # Process in batches to avoid overwhelming APIs
        batch_size = self.discovery_config["concurrent_collections"]
        total_time = 0
        
        for i in range(0, len(niches), batch_size):
            batch = niches[i:i + batch_size]
            batch_start = datetime.utcnow()
            
            # Process batch in parallel
            batch_tasks = [
                self._analyze_niche_complete(niche)
                for niche in batch
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for j, result in enumerate(batch_results):
                analysis_stats["total_processed"] += 1
                
                if isinstance(result, Exception):
                    logger.error(f"Batch analysis failed for {batch[j].name}: {result}")
                    analysis_stats["failed_analyses"] += 1
                else:
                    analysis_stats["successful_analyses"] += 1
                    analysis_stats["metrics_collected"] += result.get("metrics_count", 0)
            
            batch_time = (datetime.utcnow() - batch_start).total_seconds()
            total_time += batch_time
            
            logger.info(f"Processed batch {i//batch_size + 1}: {len(batch)} niches in {batch_time:.1f}s")
            
            # Rate limiting between batches
            await asyncio.sleep(2)
        
        if analysis_stats["total_processed"] > 0:
            analysis_stats["avg_processing_time"] = total_time / analysis_stats["total_processed"]
        
        return {"stats": analysis_stats}
    
    async def _analyze_niche_complete(self, niche: Niche) -> Dict[str, Any]:
        """Complete analysis of a single niche"""
        try:
            # Collect all metrics
            metrics_result = await self._collect_all_metrics(niche.id, niche.name, niche.keywords)
            
            # Calculate and update scores
            await self.scoring_service.update_niche_scores(niche.id)
            
            # Mark as analyzed
            niche.last_analyzed = datetime.utcnow()
            niche.is_validated = True
            await self.session.commit()
            
            return {
                "niche_id": niche.id,
                "success": True,
                "metrics_count": metrics_result.get("total_metrics", 0)
            }
            
        except Exception as e:
            logger.error(f"Error in complete analysis for {niche.name}: {e}")
            return {
                "niche_id": niche.id,
                "success": False,
                "error": str(e),
                "metrics_count": 0
            }
    
    async def _collect_all_metrics(self, niche_id: int, niche_name: str, keywords: List[str]) -> Dict[str, Any]:
        """Collect metrics from all sources for a niche"""
        metrics_result = {
            "total_metrics": 0,
            "summary": {},
            "errors": []
        }
        
        try:
            # Collect from all sources in parallel
            collection_tasks = [
                ("youtube", self.youtube_service.collect_niche_metrics(niche_id, niche_name, keywords)),
                ("google_trends", self.google_trends_service.collect_niche_trends_metrics(niche_id, niche_name, keywords)),
                ("reddit", self.reddit_service.collect_reddit_metrics(niche_id, niche_name, keywords))
            ]
            
            # Wait for all collections with timeout
            collection_results = await asyncio.wait_for(
                asyncio.gather(*[task for _, task in collection_tasks], return_exceptions=True),
                timeout=self.discovery_config["metric_collection_timeout"]
            )
            
            # Process results
            for i, (source, _) in enumerate(collection_tasks):
                result = collection_results[i]
                
                if isinstance(result, Exception):
                    error_msg = f"Error collecting from {source}: {result}"
                    logger.error(error_msg)
                    metrics_result["errors"].append(error_msg)
                    metrics_result["summary"][source] = 0
                else:
                    # Save metrics to database
                    for metric in result:
                        self.session.add(metric)
                    
                    metrics_result["summary"][source] = len(result)
                    metrics_result["total_metrics"] += len(result)
            
            await self.session.commit()
            
        except asyncio.TimeoutError:
            error_msg = f"Metric collection timeout for niche {niche_name}"
            logger.error(error_msg)
            metrics_result["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Error in metric collection: {e}"
            logger.error(error_msg)
            metrics_result["errors"].append(error_msg)
        
        return metrics_result
    
    async def _identify_high_potential_niches(self) -> List[Dict[str, Any]]:
        """Identify niches with high potential (80+ score)"""
        threshold = self.discovery_config["high_potential_threshold"]
        
        query = select(Niche).where(
            and_(
                Niche.overall_score >= threshold,
                Niche.is_validated == True
            )
        ).order_by(Niche.overall_score.desc()).limit(20)
        
        result = await self.session.execute(query)
        high_potential_niches = result.scalars().all()
        
        niche_data = []
        for niche in high_potential_niches:
            score_breakdown = await self.scoring_service.get_niche_score_breakdown(niche.id)
            
            niche_data.append({
                "id": niche.id,
                "name": niche.name,
                "description": niche.description,
                "category": niche.category,
                "overall_score": niche.overall_score,
                "grade": score_breakdown["grade"],
                "discovery_source": niche.discovery_source,
                "last_analyzed": niche.last_analyzed.isoformat(),
                "top_recommendations": score_breakdown["recommendations"][:3]
            })
        
        return niche_data
    
    async def _generate_discovery_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from discovery session"""
        insights = {
            "performance_summary": analysis_results.get("stats", {}),
            "trending_categories": await self._get_trending_categories(),
            "market_opportunities": await self._identify_market_gaps(),
            "recommendation_summary": await self._generate_action_recommendations()
        }
        
        return insights
    
    async def _generate_market_insights(self, niche_id: int, niche_name: str) -> Dict[str, Any]:
        """Generate detailed market insights for a niche"""
        insights = {
            "competition_analysis": {},
            "monetization_potential": {},
            "content_opportunities": {},
            "market_trends": {}
        }
        
        try:
            # Get recent metrics for analysis
            query = select(Metric).where(
                and_(
                    Metric.niche_id == niche_id,
                    Metric.collected_at >= datetime.utcnow() - timedelta(hours=24)
                )
            )
            result = await self.session.execute(query)
            metrics = result.scalars().all()
            
            # Organize metrics by type
            metric_groups = {}
            for metric in metrics:
                metric_type = metric.metric_type
                if metric_type not in metric_groups:
                    metric_groups[metric_type] = []
                metric_groups[metric_type].append(metric)
            
            # Generate insights from each metric type
            for metric_type, type_metrics in metric_groups.items():
                if metric_type == "competition":
                    insights["competition_analysis"] = self._analyze_competition_metrics(type_metrics)
                elif metric_type == "search_volume":
                    insights["market_trends"] = self._analyze_trend_metrics(type_metrics)
                elif metric_type == "content_opportunity":
                    insights["content_opportunities"] = self._analyze_content_metrics(type_metrics)
        
        except Exception as e:
            logger.error(f"Error generating market insights: {e}")
        
        return insights
    
    def _deduplicate_niches(self, niches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate niches based on name similarity"""
        unique_niches = []
        seen_names = set()
        
        for niche in niches:
            name = niche.get("name", "").lower().strip()
            
            # Simple deduplication - could be enhanced with fuzzy matching
            if name and name not in seen_names:
                seen_names.add(name)
                unique_niches.append(niche)
        
        return unique_niches
    
    async def _create_or_get_niche(self, niche_name: str, keywords: List[str]) -> Niche:
        """Create a new niche or get existing one"""
        # Check if niche already exists
        query = select(Niche).where(Niche.name.ilike(f"%{niche_name}%"))
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # Create new niche
        niche = Niche(
            name=niche_name,
            description=f"Niche analysis for {niche_name}",
            category="Manual Analysis",
            keywords=keywords,
            discovery_source="manual",
            is_active=True,
            discovered_at=datetime.utcnow(),
            last_analyzed=datetime.utcnow()
        )
        
        self.session.add(niche)
        await self.session.commit()
        return niche
    
    async def _get_trending_categories(self) -> List[Dict[str, Any]]:
        """Get trending categories from recent discoveries"""
        # Implementation for category trending analysis
        return []
    
    async def _identify_market_gaps(self) -> List[Dict[str, Any]]:
        """Identify market gaps and opportunities"""
        # Implementation for market gap analysis
        return []
    
    async def _generate_action_recommendations(self) -> List[str]:
        """Generate actionable recommendations from analysis"""
        # Implementation for recommendation generation
        return []
    
    def _analyze_competition_metrics(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze competition-related metrics"""
        return {"summary": "Competition analysis pending"}
    
    def _analyze_trend_metrics(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze trend-related metrics"""
        return {"summary": "Trend analysis pending"}
    
    def _analyze_content_metrics(self, metrics: List[Metric]) -> Dict[str, Any]:
        """Analyze content opportunity metrics"""
        return {"summary": "Content analysis pending"}