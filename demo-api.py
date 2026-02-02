#!/usr/bin/env python3
"""
YouTube Niche Discovery Engine - Standalone Demo API
PM Agent Implementation - Immediate Demo Version

This is a simplified version that runs without database dependencies
to demonstrate the core PM algorithm functionality immediately.
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================================================
# PM AGENT'S 100-POINT SCORING ALGORITHM - EXACT IMPLEMENTATION
# ============================================================================

@dataclass
class PMMetrics:
    """PM Agent's metrics for niche scoring"""
    google_trends_score: float = 70.0
    youtube_monthly_searches: int = 250000
    channels_per_million_searches: float = 120.0
    avg_monthly_subscriber_growth: float = 12.0
    estimated_cpm: float = 4.5
    brand_safety_score: float = 4.0
    reddit_subreddit_members: int = 75000
    tiktok_hashtag_posts: int = 2500000
    news_coverage_frequency: float = 3.0
    yearly_growth_rate: float = 25.0
    social_momentum_score: float = 65.0

class PMScoringAlgorithm:
    """
    PM Agent's 100-Point Scoring Algorithm
    EXACT implementation from PM_DELIVERABLES.md
    """
    
    def __init__(self):
        # PM Agent's CPM tiers
        self.cpm_tiers = {
            "tier_1": {"min_cpm": 10.0, "points": 15, "categories": ["finance", "business", "marketing", "investing"]},
            "tier_2": {"min_cpm": 4.0, "points": 12, "categories": ["education", "tech", "science", "lifestyle"]},
            "tier_3": {"min_cpm": 2.0, "points": 9, "categories": ["beauty", "fashion", "gaming", "entertainment"]},
            "tier_4": {"min_cpm": 1.0, "points": 6, "categories": ["fitness", "bodybuilding"]},
            "tier_5": {"min_cpm": 0.0, "points": 3, "categories": ["comedy", "music", "pranks"]}
        }
    
    def calculate_score(self, niche_name: str, category: str, metrics: PMMetrics) -> Dict[str, float]:
        """Calculate PM Agent's exact 100-point score"""
        
        # 1. Search Volume (25 points)
        search_volume_score = self._calculate_search_volume_score(metrics)
        
        # 2. Competition (25 points - inverse)
        competition_score = self._calculate_competition_score(metrics)
        
        # 3. Monetization (20 points)
        monetization_score = self._calculate_monetization_score(category, metrics)
        
        # 4. Content Availability (15 points)
        content_availability_score = self._calculate_content_availability_score(metrics)
        
        # 5. Trend Momentum (15 points)
        trend_momentum_score = self._calculate_trend_momentum_score(metrics)
        
        # Calculate overall score
        overall_score = (
            search_volume_score +
            competition_score +
            monetization_score +
            content_availability_score +
            trend_momentum_score
        )
        
        return {
            "overall_score": round(min(100, max(0, overall_score)), 2),
            "search_volume_score": round(search_volume_score, 2),
            "competition_score": round(competition_score, 2),
            "monetization_score": round(monetization_score, 2),
            "content_availability_score": round(content_availability_score, 2),
            "trend_momentum_score": round(trend_momentum_score, 2),
            "breakdown": {
                "search_volume": {"score": search_volume_score, "max": 25},
                "competition": {"score": competition_score, "max": 25},
                "monetization": {"score": monetization_score, "max": 20},
                "content_availability": {"score": content_availability_score, "max": 15},
                "trend_momentum": {"score": trend_momentum_score, "max": 15}
            }
        }
    
    def _calculate_search_volume_score(self, metrics: PMMetrics) -> float:
        """Search Volume (25 points): Google Trends + YouTube searches"""
        google_trends_points = 0.0
        youtube_search_points = 0.0
        
        # Google Trends (15 points max)
        if metrics.google_trends_score >= 90:
            google_trends_points = 15.0
        elif metrics.google_trends_score >= 70:
            google_trends_points = 12.0
        elif metrics.google_trends_score >= 50:
            google_trends_points = 9.0
        elif metrics.google_trends_score >= 30:
            google_trends_points = 6.0
        else:
            google_trends_points = 3.0
        
        # YouTube searches (10 points max)
        if metrics.youtube_monthly_searches >= 1_000_000:
            youtube_search_points = 10.0
        elif metrics.youtube_monthly_searches >= 500_000:
            youtube_search_points = 8.0
        elif metrics.youtube_monthly_searches >= 100_000:
            youtube_search_points = 6.0
        elif metrics.youtube_monthly_searches >= 50_000:
            youtube_search_points = 4.0
        else:
            youtube_search_points = 2.0
        
        return google_trends_points + youtube_search_points
    
    def _calculate_competition_score(self, metrics: PMMetrics) -> float:
        """Competition (25 points - inverse): Channel saturation + growth rate"""
        saturation_points = 0.0
        growth_points = 0.0
        
        # Channel saturation (15 points max)
        if metrics.channels_per_million_searches < 50:
            saturation_points = 15.0
        elif metrics.channels_per_million_searches < 100:
            saturation_points = 12.0
        elif metrics.channels_per_million_searches < 200:
            saturation_points = 9.0
        elif metrics.channels_per_million_searches < 500:
            saturation_points = 6.0
        else:
            saturation_points = 3.0
        
        # Subscriber growth rate (10 points max)
        if metrics.avg_monthly_subscriber_growth < 5:
            growth_points = 10.0
        elif metrics.avg_monthly_subscriber_growth < 10:
            growth_points = 8.0
        elif metrics.avg_monthly_subscriber_growth < 20:
            growth_points = 6.0
        elif metrics.avg_monthly_subscriber_growth < 30:
            growth_points = 4.0
        else:
            growth_points = 2.0
        
        return saturation_points + growth_points
    
    def _calculate_monetization_score(self, category: str, metrics: PMMetrics) -> float:
        """Monetization (20 points): CPM rate + brand safety"""
        cpm_points = 0.0
        brand_safety_points = min(metrics.brand_safety_score, 5.0)
        
        # CPM rate tier (15 points max)
        if metrics.estimated_cpm >= 10.0:
            cmp_points = 15.0
        elif metrics.estimated_cpm >= 4.0:
            cmp_points = 12.0
        elif metrics.estimated_cpm >= 2.0:
            cmp_points = 9.0
        elif metrics.estimated_cpm >= 1.0:
            cmp_points = 6.0
        else:
            cmp_points = 3.0
        
        return cmp_points + brand_safety_points
    
    def _calculate_content_availability_score(self, metrics: PMMetrics) -> float:
        """Content Availability (15 points): Reddit + TikTok + news"""
        reddit_points = 0.0
        tiktok_points = 0.0
        news_points = 0.0
        
        # Reddit (5 points max)
        if metrics.reddit_subreddit_members >= 100_000:
            reddit_points = 5.0
        elif metrics.reddit_subreddit_members >= 50_000:
            reddit_points = 4.0
        elif metrics.reddit_subreddit_members >= 10_000:
            reddit_points = 3.0
        elif metrics.reddit_subreddit_members >= 1_000:
            reddit_points = 2.0
        else:
            reddit_points = 1.0
        
        # TikTok (5 points max)
        if metrics.tiktok_hashtag_posts >= 10_000_000:
            tiktok_points = 5.0
        elif metrics.tiktok_hashtag_posts >= 1_000_000:
            tiktok_points = 4.0
        elif metrics.tiktok_hashtag_posts >= 100_000:
            tiktok_points = 3.0
        elif metrics.tiktok_hashtag_posts >= 10_000:
            tiktok_points = 2.0
        else:
            tiktok_points = 1.0
        
        # News coverage (5 points max)
        news_points = min(metrics.news_coverage_frequency, 5.0)
        
        return reddit_points + tiktok_points + news_points
    
    def _calculate_trend_momentum_score(self, metrics: PMMetrics) -> float:
        """Trend Momentum (15 points): 12-month growth + social momentum"""
        growth_points = 0.0
        social_points = 0.0
        
        # 12-month growth (10 points max)
        if metrics.yearly_growth_rate >= 50:
            growth_points = 10.0
        elif metrics.yearly_growth_rate >= 20:
            growth_points = 8.0
        elif metrics.yearly_growth_rate >= 0:
            growth_points = 6.0
        elif metrics.yearly_growth_rate >= -20:
            growth_points = 4.0
        else:
            growth_points = 2.0
        
        # Social momentum (5 points max)
        social_points = min(metrics.social_momentum_score / 20, 5.0)
        
        return growth_points + social_points

# ============================================================================
# DEMO DATA GENERATOR
# ============================================================================

class DemoNicheGenerator:
    """Generate demo niches with realistic PM scoring"""
    
    def __init__(self):
        self.scorer = PMScoringAlgorithm()
        self.demo_niches = [
            # Tier 1: High-value niches (PM Agent favorites)
            {"name": "ai passive income", "category": "finance", "base_cpm": 15.0, "trend_multiplier": 1.2},
            {"name": "crypto trading strategies", "category": "finance", "base_cpm": 18.0, "trend_multiplier": 1.1},
            {"name": "affiliate marketing automation", "category": "business", "base_cpm": 22.0, "trend_multiplier": 1.3},
            {"name": "digital product creation", "category": "business", "base_cpm": 12.0, "trend_multiplier": 1.15},
            
            # Tier 2: Strong performers
            {"name": "ai productivity tools", "category": "tech", "base_cpm": 8.0, "trend_multiplier": 1.25},
            {"name": "python automation tutorials", "category": "education", "base_cpm": 5.5, "trend_multiplier": 1.1},
            {"name": "sustainable living hacks", "category": "lifestyle", "base_cpm": 4.2, "trend_multiplier": 1.05},
            
            # Tier 3: Moderate opportunities
            {"name": "vegan meal prep", "category": "cooking", "base_cpm": 2.8, "trend_multiplier": 0.95},
            {"name": "minimalist fashion", "category": "fashion", "base_cpm": 3.1, "trend_multiplier": 1.0},
            {"name": "indie game development", "category": "gaming", "base_cpm": 2.9, "trend_multiplier": 0.9},
        ]
    
    def generate_niche_with_metrics(self, niche_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a niche with realistic metrics"""
        name = niche_data["name"]
        category = niche_data["category"]
        base_cpm = niche_data["base_cpm"]
        trend_multiplier = niche_data["trend_multiplier"]
        
        # Generate realistic metrics based on niche type
        metrics = self._generate_realistic_metrics(name, category, base_cpm, trend_multiplier)
        
        # Calculate PM score
        scores = self.scorer.calculate_score(name, category, metrics)
        
        return {
            "id": abs(hash(name)) % 10000,
            "name": name,
            "category": category,
            "description": f"AI-discovered niche: {name}",
            "scores": scores,
            "metrics": asdict(metrics),
            "discovered_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "pm_algorithm_version": "1.0"
        }
    
    def _generate_realistic_metrics(self, name: str, category: str, base_cpm: float, trend_multiplier: float) -> PMMetrics:
        """Generate realistic metrics for a niche"""
        # Use name hash for consistent randomization
        seed = abs(hash(name)) % 1000
        
        # Google Trends based on niche popularity
        google_trends = min(95, 40 + (seed % 60) * trend_multiplier)
        
        # YouTube searches based on trends
        youtube_searches = int(50000 + (seed % 500000) * trend_multiplier)
        
        # Competition based on niche saturation
        competition = min(800, 50 + (seed % 300))
        if "ai" in name or "crypto" in name:
            competition *= 1.5  # Higher competition for hot topics
        
        # Growth rate based on trend
        growth_rate = max(-10, (seed % 40) * trend_multiplier - 15)
        
        # Social metrics
        reddit_members = int(10000 + (seed % 200000))
        tiktok_posts = int(100000 + (seed % 10000000))
        news_frequency = min(5, 1 + (seed % 4))
        
        # Brand safety based on category
        brand_safety = 5.0
        if category in ["finance", "education", "health"]:
            brand_safety = 5.0
        elif category in ["gaming", "entertainment"]:
            brand_safety = 3.5
        else:
            brand_safety = 4.0
        
        return PMMetrics(
            google_trends_score=google_trends,
            youtube_monthly_searches=youtube_searches,
            channels_per_million_searches=competition,
            avg_monthly_subscriber_growth=growth_rate,
            estimated_cpm=base_cpm,
            brand_safety_score=brand_safety,
            reddit_subreddit_members=reddit_members,
            tiktok_hashtag_posts=tiktok_posts,
            news_coverage_frequency=news_frequency,
            yearly_growth_rate=growth_rate * 2,
            social_momentum_score=min(100, 30 + (seed % 50))
        )

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Pydantic models
class NicheResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    scores: Dict[str, Any]
    metrics: Dict[str, Any]
    discovered_at: str
    last_updated: str

class DashboardStats(BaseModel):
    summary: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    generated_at: str

# FastAPI app
app = FastAPI(
    title="YouTube Niche Discovery Engine - PM Agent Demo",
    description="PM Agent's 100-Point Scoring Algorithm Implementation",
    version="1.0.0"
)

# CORS for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data
demo_generator = DemoNicheGenerator()
cached_niches = []

# Generate demo niches on startup
for niche_data in demo_generator.demo_niches:
    niche = demo_generator.generate_niche_with_metrics(niche_data)
    cached_niches.append(niche)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "message": "YouTube Niche Discovery Engine - PM Agent Demo",
        "version": "1.0.0",
        "algorithm": "PM Agent 100-Point Scoring",
        "status": "live",
        "server_ip": "38.143.19.241",
        "endpoints": {
            "docs": "/docs",
            "niches": "/api/v1/niches/",
            "high_potential": "/api/v1/niches/high-potential/",
            "dashboard": "/api/v1/niches/dashboard/stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "pm_algorithm": "active",
        "demo_niches": len(cached_niches)
    }

@app.get("/api/v1/niches/", response_model=List[NicheResponse])
async def get_niches(limit: int = 20, min_score: float = 0.0):
    """Get all niches"""
    filtered_niches = [
        niche for niche in cached_niches 
        if niche["scores"]["overall_score"] >= min_score
    ]
    sorted_niches = sorted(filtered_niches, key=lambda x: x["scores"]["overall_score"], reverse=True)
    return sorted_niches[:limit]

@app.get("/api/v1/niches/high-potential/")
async def get_high_potential_niches(limit: int = 10):
    """Get high-potential niches (90+ score)"""
    high_potential = [
        {
            "id": niche["id"],
            "name": niche["name"],
            "score": niche["scores"]["overall_score"],
            "category": niche["category"],
            "discovered_at": niche["discovered_at"],
            "score_breakdown": niche["scores"]["breakdown"]
        }
        for niche in cached_niches 
        if niche["scores"]["overall_score"] >= 90.0
    ]
    return sorted(high_potential, key=lambda x: x["score"], reverse=True)[:limit]

@app.get("/api/v1/niches/{niche_id}")
async def get_niche(niche_id: int):
    """Get specific niche"""
    niche = next((n for n in cached_niches if n["id"] == niche_id), None)
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    return niche

@app.post("/api/v1/niches/discover/daily")
async def discover_niches_daily():
    """Trigger daily discovery (demo simulation)"""
    return {
        "message": "Daily discovery started (demo mode)",
        "status": "processing",
        "target": "100+ niches",
        "algorithm": "PM Agent 100-point scoring",
        "demo_note": "In production, this would discover real niches from YouTube, TikTok, and Reddit",
        "started_at": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/niches/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_niches = len(cached_niches)
    high_potential = len([n for n in cached_niches if n["scores"]["overall_score"] >= 90])
    medium_potential = len([n for n in cached_niches if 70 <= n["scores"]["overall_score"] < 90])
    avg_score = sum(n["scores"]["overall_score"] for n in cached_niches) / total_niches if total_niches > 0 else 0
    
    return {
        "summary": {
            "total_niches": total_niches,
            "high_potential": high_potential,
            "medium_potential": medium_potential,
            "recent_discoveries_24h": total_niches,  # Demo data
            "average_score": round(avg_score, 2)
        },
        "performance_metrics": {
            "high_potential_rate": round((high_potential / max(total_niches, 1)) * 100, 1),
            "discovery_target_progress": f"{total_niches}/100",
            "algorithm_effectiveness": round(avg_score, 1)
        },
        "category_distribution": [
            {"category": "finance", "count": len([n for n in cached_niches if n["category"] == "finance"])},
            {"category": "business", "count": len([n for n in cached_niches if n["category"] == "business"])},
            {"category": "tech", "count": len([n for n in cached_niches if n["category"] == "tech"])},
            {"category": "education", "count": len([n for n in cached_niches if n["category"] == "education"])},
            {"category": "lifestyle", "count": len([n for n in cached_niches if n["category"] == "lifestyle"])}
        ],
        "generated_at": datetime.utcnow().isoformat(),
        "demo_mode": True,
        "pm_algorithm_version": "1.0"
    }

@app.get("/api/v1/niches/{niche_id}/score-breakdown")
async def get_score_breakdown(niche_id: int):
    """Get detailed PM score breakdown"""
    niche = next((n for n in cached_niches if n["id"] == niche_id), None)
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    scores = niche["scores"]
    return {
        "niche_id": niche_id,
        "niche_name": niche["name"],
        "pm_algorithm_breakdown": {
            "overall_score": scores["overall_score"],
            "components": {
                "search_volume": {
                    "score": scores["search_volume_score"],
                    "max_points": 25,
                    "percentage": round((scores["search_volume_score"] / 25) * 100, 1),
                    "description": "Google Trends + YouTube search volume"
                },
                "competition": {
                    "score": scores["competition_score"],
                    "max_points": 25,
                    "percentage": round((scores["competition_score"] / 25) * 100, 1),
                    "description": "Channel saturation + subscriber growth (inverse)"
                },
                "monetization": {
                    "score": scores["monetization_score"],
                    "max_points": 20,
                    "percentage": round((scores["monetization_score"] / 20) * 100, 1),
                    "description": "CPM rates + brand safety"
                },
                "content_availability": {
                    "score": scores["content_availability_score"],
                    "max_points": 15,
                    "percentage": round((scores["content_availability_score"] / 15) * 100, 1),
                    "description": "Reddit + TikTok + news coverage"
                },
                "trend_momentum": {
                    "score": scores["trend_momentum_score"],
                    "max_points": 15,
                    "percentage": round((scores["trend_momentum_score"] / 15) * 100, 1),
                    "description": "12-month growth + social momentum"
                }
            }
        },
        "performance_indicators": {
            "is_high_potential": scores["overall_score"] >= 90,
            "is_viable": scores["overall_score"] >= 50,
            "risk_level": "low" if scores["overall_score"] >= 80 else "medium" if scores["overall_score"] >= 60 else "high",
            "recommendation": "IMMEDIATE ACTION" if scores["overall_score"] >= 90 else "CONSIDER" if scores["overall_score"] >= 70 else "RESEARCH MORE" if scores["overall_score"] >= 50 else "SKIP"
        },
        "last_calculated": datetime.utcnow().isoformat(),
        "pm_algorithm_version": "1.0"
    }

if __name__ == "__main__":
    print("🚀 Starting YouTube Niche Discovery Engine - PM Agent Demo")
    print("🌍 Server IP: 38.143.19.241")
    print("🔌 Backend: http://38.143.19.241:8000")
    print("📖 Documentation: http://38.143.19.241:8000/docs")
    print("🎯 PM Algorithm: ACTIVE - 100-point scoring system")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )