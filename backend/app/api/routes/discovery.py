"""
Discovery API Routes - Main niche discovery functionality
"""

import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.schemas.niche import NicheResponse
from app.services.discovery import NicheDiscoveryEngine
from app.services.scoring import NicheScorer, NicheMetrics

router = APIRouter()

# Global discovery engine instance
discovery_engine = NicheDiscoveryEngine()

@router.post("/discover")
async def discover_niches(
    background_tasks: BackgroundTasks,
    sources: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    min_score_threshold: float = 50.0,
    limit: int = 20,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Discover and score profitable niches
    """
    try:
        # Run discovery
        discovered_niches = await discovery_engine.discover_niches(
            sources=sources,
            limit=limit,
            min_score_threshold=min_score_threshold
        )
        
        # Format response
        results = []
        for niche in discovered_niches:
            results.append({
                "niche_name": niche["niche_name"],
                "total_score": niche["score"]["total_score"],
                "grade": niche["score"]["grade"],
                "recommendation": niche["score"]["recommendation"],
                "risk_level": niche["score"]["risk_level"],
                "metrics": niche["metrics"],
                "breakdown": niche["score"]["breakdown"],
                "analyzed_at": niche["analyzed_at"],
                "data_sources": niche["data_sources"]
            })
        
        return {
            "status": "success",
            "discovered_count": len(results),
            "niches": results,
            "parameters": {
                "sources": sources or ["youtube", "tiktok", "reddit", "google_trends"],
                "min_score_threshold": min_score_threshold,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@router.get("/status")
async def get_discovery_status():
    """Get current status of discovery system"""
    return {
        "status": "ready",
        "services": {
            "youtube_scraper": "active",
            "google_trends": "active", 
            "reddit_scraper": "active",
            "tiktok_scraper": "active"
        },
        "last_run": None,
        "total_discovered_today": 0,
        "system_health": "healthy"
    }

@router.get("/trending")
async def get_trending_niches(
    limit: int = 20,
    source: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session)
):
    """Get currently trending niches across platforms"""
    try:
        trending_data = {}
        
        # Get trending from each platform
        if not source or source == "youtube":
            youtube_trending = await discovery_engine.youtube_scraper.get_trending_topics()
            trending_data["youtube"] = youtube_trending[:limit//4]
        
        if not source or source == "tiktok":
            tiktok_trending = await discovery_engine.tiktok_scraper.get_trending_hashtags()
            trending_data["tiktok"] = tiktok_trending[:limit//4]
        
        if not source or source == "google_trends":
            trends_trending = await discovery_engine.trends_scraper.get_trending_topics()
            trending_data["google_trends"] = trends_trending[:limit//4]
        
        if not source or source == "reddit":
            reddit_trending = await discovery_engine.reddit_scraper.get_growing_topics()
            trending_data["reddit"] = reddit_trending[:limit//4]
        
        return {
            "trending_niches": trending_data,
            "updated_at": "2024-02-02T15:00:00Z",
            "total_sources": len(trending_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending niches: {str(e)}")

@router.post("/analyze")
async def analyze_niche(
    niche_name: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Analyze a specific niche manually"""
    try:
        # Analyze the niche
        analysis = await discovery_engine._analyze_niche(niche_name)
        
        if not analysis:
            raise HTTPException(status_code=404, detail=f"Could not analyze niche: {niche_name}")
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/metrics/{niche_name}")
async def get_niche_metrics(
    niche_name: str,
    include_details: bool = True
):
    """Get detailed metrics for a specific niche"""
    try:
        # Get metrics from all sources
        tasks = [
            discovery_engine._get_youtube_metrics(niche_name),
            discovery_engine._get_trends_metrics(niche_name),
            discovery_engine._get_reddit_metrics(niche_name),
            discovery_engine._get_tiktok_metrics(niche_name)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics = {
            "niche_name": niche_name,
            "youtube": results[0] if not isinstance(results[0], Exception) else None,
            "google_trends": results[1] if not isinstance(results[1], Exception) else None,
            "reddit": results[2] if not isinstance(results[2], Exception) else None,
            "tiktok": results[3] if not isinstance(results[3], Exception) else None,
            "retrieved_at": "2024-02-02T15:00:00Z"
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/score")
async def score_niche_manually(
    search_volume: int,
    google_trends_score: int,
    channel_count: int,
    avg_subscriber_growth: float,
    cpm_estimate: float,
    brand_safety_level: str = "family",
    reddit_members: int = 0,
    tiktok_posts: int = 0,
    news_coverage: str = "occasional",
    trend_growth_12m: float = 0.0,
    social_sentiment: float = 0.5
):
    """Score a niche manually with provided metrics"""
    try:
        # Create metrics object
        metrics = NicheMetrics(
            search_volume=search_volume,
            google_trends_score=google_trends_score,
            channel_count=channel_count,
            avg_subscriber_growth=avg_subscriber_growth,
            cmp_estimate=cpm_estimate,
            brand_safety_level=brand_safety_level,
            reddit_members=reddit_members,
            tiktok_posts=tiktok_posts,
            news_coverage=news_coverage,
            trend_growth_12m=trend_growth_12m,
            social_sentiment=social_sentiment
        )
        
        # Calculate score
        scorer = NicheScorer()
        score_result = scorer.calculate_total_score(metrics)
        
        return {
            "status": "success",
            "score": score_result,
            "input_metrics": {
                "search_volume": search_volume,
                "google_trends_score": google_trends_score,
                "channel_count": channel_count,
                "avg_subscriber_growth": avg_subscriber_growth,
                "cpm_estimate": cmp_estimate,
                "brand_safety_level": brand_safety_level,
                "reddit_members": reddit_members,
                "tiktok_posts": tiktok_posts,
                "news_coverage": news_coverage,
                "trend_growth_12m": trend_growth_12m,
                "social_sentiment": social_sentiment
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.get("/quick-test")
async def quick_test():
    """Quick test endpoint to verify discovery system"""
    try:
        # Test with a few sample niches
        sample_niches = ["AI tutorials", "passive income", "productivity hacks"]
        
        results = []
        for niche in sample_niches:
            analysis = await discovery_engine._analyze_niche(niche)
            if analysis:
                results.append({
                    "niche": niche,
                    "score": analysis["score"]["total_score"],
                    "grade": analysis["score"]["grade"],
                    "recommendation": analysis["score"]["recommendation"]
                })
        
        return {
            "status": "success", 
            "test_results": results,
            "system_status": "operational",
            "tested_at": "2024-02-02T15:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

@router.get("/categories")
async def get_niche_categories():
    """Get available niche categories"""
    categories = {
        "business": ["entrepreneurship", "marketing", "sales", "e-commerce"],
        "finance": ["investing", "personal finance", "crypto", "passive income"],
        "technology": ["AI", "programming", "tech reviews", "tutorials"],
        "lifestyle": ["productivity", "health", "fitness", "travel"],
        "education": ["online learning", "skill development", "career advice"],
        "entertainment": ["gaming", "music", "comedy", "viral content"],
        "creative": ["design", "photography", "art", "content creation"]
    }
    
    return {
        "categories": categories,
        "total_categories": len(categories)
    }