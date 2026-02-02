#!/usr/bin/env python3
"""
Initialize Database with Sample Data
"""

import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import async_session, create_all_tables
from backend.app.models.source import Source
from backend.app.models.niche import Niche
from backend.app.models.metric import Metric

async def init_sample_data():
    """Initialize database with sample data"""
    print("🚀 Initializing database with sample data...")
    
    async with async_session() as session:
        try:
            # Create tables first
            print("📊 Creating database tables...")
            await create_all_tables()
            
            # Add sample sources
            print("🔗 Adding sample sources...")
            sources_data = [
                {
                    "name": "youtube",
                    "display_name": "YouTube",
                    "description": "YouTube Data API and web scraping",
                    "base_url": "https://www.googleapis.com/youtube/v3",
                    "requires_auth": True,
                    "auth_type": "api_key",
                    "requests_per_minute": 100,
                    "requests_per_hour": 10000,
                    "requests_per_day": 1000000
                },
                {
                    "name": "tiktok",
                    "display_name": "TikTok",
                    "description": "TikTok trending and hashtag analysis",
                    "base_url": "https://www.tiktok.com",
                    "requires_auth": False,
                    "auth_type": None,
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "requests_per_day": 10000
                },
                {
                    "name": "reddit",
                    "display_name": "Reddit",
                    "description": "Reddit API for subreddit analysis",
                    "base_url": "https://www.reddit.com",
                    "requires_auth": True,
                    "auth_type": "oauth",
                    "requests_per_minute": 60,
                    "requests_per_hour": 3600,
                    "requests_per_day": 86400
                },
                {
                    "name": "google_trends",
                    "display_name": "Google Trends",
                    "description": "Google Trends data analysis",
                    "base_url": "https://trends.google.com",
                    "requires_auth": False,
                    "auth_type": None,
                    "requests_per_minute": 30,
                    "requests_per_hour": 1000,
                    "requests_per_day": 10000
                }
            ]
            
            for source_data in sources_data:
                # Check if source already exists
                from sqlalchemy import select
                existing_query = select(Source).where(Source.name == source_data["name"])
                result = await session.execute(existing_query)
                existing = result.scalar_one_or_none()
                
                if not existing:
                    source = Source(**source_data)
                    session.add(source)
                    print(f"  ✅ Added source: {source_data['display_name']}")
                else:
                    print(f"  ⏭️  Source already exists: {source_data['display_name']}")
            
            # Add sample niches
            print("🎯 Adding sample niches...")
            sample_niches = [
                {
                    "name": "AI Art Creation",
                    "description": "Creating art using artificial intelligence tools",
                    "keywords": ["AI art", "midjourney", "stable diffusion", "digital art", "AI creativity"],
                    "category": "Technology",
                    "overall_score": 85.5,
                    "trend_score": 90.0,
                    "competition_score": 75.0,
                    "monetization_score": 80.0,
                    "audience_score": 88.0,
                    "content_opportunity_score": 85.0,
                    "discovery_source": "youtube",
                    "discovery_method": "trending_analysis"
                },
                {
                    "name": "Minimalist Lifestyle",
                    "description": "Living with less stuff and more intention",
                    "keywords": ["minimalism", "declutter", "simple living", "tiny house", "mindful living"],
                    "category": "Lifestyle",
                    "overall_score": 78.2,
                    "trend_score": 75.0,
                    "competition_score": 70.0,
                    "monetization_score": 82.0,
                    "audience_score": 85.0,
                    "content_opportunity_score": 79.0,
                    "discovery_source": "reddit",
                    "discovery_method": "subreddit_analysis"
                },
                {
                    "name": "Home Workout Equipment Reviews",
                    "description": "Reviewing fitness equipment for home use",
                    "keywords": ["home gym", "workout equipment", "fitness gear", "exercise reviews", "home fitness"],
                    "category": "Fitness",
                    "overall_score": 92.1,
                    "trend_score": 95.0,
                    "competition_score": 85.0,
                    "monetization_score": 96.0,
                    "audience_score": 90.0,
                    "content_opportunity_score": 94.0,
                    "discovery_source": "google_trends",
                    "discovery_method": "trend_analysis"
                }
            ]
            
            for niche_data in sample_niches:
                # Check if niche already exists
                existing_query = select(Niche).where(Niche.name == niche_data["name"])
                result = await session.execute(existing_query)
                existing = result.scalar_one_or_none()
                
                if not existing:
                    niche = Niche(**niche_data)
                    session.add(niche)
                    print(f"  ✅ Added niche: {niche_data['name']}")
                else:
                    print(f"  ⏭️  Niche already exists: {niche_data['name']}")
            
            # Commit all changes
            await session.commit()
            print("✅ Sample data initialization completed!")
            
            # Print summary
            sources_count = await session.execute(select(Source))
            niches_count = await session.execute(select(Niche))
            
            print(f"\n📈 Database Summary:")
            print(f"  - Sources: {len(sources_count.scalars().all())}")
            print(f"  - Niches: {len(niches_count.scalars().all())}")
            
        except Exception as e:
            print(f"❌ Error initializing data: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(init_sample_data())