#!/usr/bin/env python3
"""Demo example showing Rising Star Channels discovery in action"""

import sys
import os
import json

# Add the directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_server import get_shared_components

def demo_rising_star_channels():
    """Demo the Rising Star Channels feature with example output"""
    print("🌟 Rising Star Channels Discovery - Demo")
    print("=" * 50)
    print()
    
    # Get components (this initializes everything)
    cache, youtube_api, trends_api, niche_scorer, recommendation_engine, channel_discovery = get_shared_components()
    
    print("✅ YouTube Niche Discovery Engine Initialized")
    print(f"🔑 API Key: ...{youtube_api.api_key[-4:]}")
    print()
    
    # Example niches to test
    example_niches = [
        "japanese tv show",
        "ai tutorial", 
        "fitness for beginners"
    ]
    
    for niche in example_niches:
        print(f"🎯 Discovering rising star channels for: '{niche}'")
        print("-" * 40)
        
        try:
            # This would normally call the real API, but will fail with demo key
            # So we'll show what the response structure looks like
            result = channel_discovery.find_rising_star_channels(niche, max_results=10)
            
            if result['success']:
                print(f"✅ Found {len(result['channels'])} rising star channels")
                for i, channel in enumerate(result['channels'][:3], 1):
                    print(f"{i}. {channel['name']} (Score: {channel['rising_star_score']})")
            else:
                print(f"❌ {result['analysis']['error_reason']}")
                print("💡 This is expected with the demo API key - quota exhausted")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 This is expected with the demo API key")
            
        print()
    
    # Show what a successful response looks like
    print("📄 Example API Response Format:")
    print("=" * 50)
    
    example_response = {
        "niche": "japanese tv show",
        "channels": [
            {
                "name": "JDrama Reactions",
                "channel_id": "UC123456789",
                "url": "https://youtube.com/channel/UC123456789",
                "subscribers": 12500,
                "total_views": 2500000,
                "video_count": 45,
                "created_date": "2024-03-15",
                "channel_age": "10 months",
                "views_per_subscriber": 200.0,
                "rising_star_score": 85.0,
                "why_rising_star": "⭐ High viral potential (200 views/sub), small channel (good opportunity)",
                "score_breakdown": {
                    "viral_potential": 35,
                    "opportunity_size": 25,
                    "age_factor": 25
                }
            },
            {
                "name": "Anime Behind Scenes",
                "channel_id": "UC987654321", 
                "url": "https://youtube.com/channel/UC987654321",
                "subscribers": 8200,
                "total_views": 1200000,
                "video_count": 32,
                "created_date": "2023-08-20",
                "channel_age": "1.3 years", 
                "views_per_subscriber": 146.3,
                "rising_star_score": 75.0,
                "why_rising_star": "⭐ Good viral potential (146 views/sub), small channel (good opportunity)"
            }
        ],
        "analysis": {
            "total_channels_found": 15,
            "rising_stars_identified": 2,
            "best_opportunity": "JDrama Reactions",
            "analysis_time": 2.4
        },
        "success": True
    }
    
    print(json.dumps(example_response, indent=2))
    
    print()
    print("🚀 Integration Points:")
    print("=" * 50)
    print("1. 🌐 New API Endpoint: GET /api/channels?niche=japanese%20tv%20show")
    print("2. 📊 Integrated Analysis: Rising star channels included in /api/analyze")  
    print("3. 🎨 UI Enhancement: New 'Rising Star Channels' section in results")
    print("4. ⚡ Smart Caching: 1-hour TTL for channel search & statistics")
    print("5. 📈 Scoring Algorithm: Views/Sub ratio + Channel size + Age factor")
    print()
    
    print("✨ Features Implemented:")
    print("=" * 50)
    print("✅ YouTube Data API integration for channel search")
    print("✅ Channel statistics retrieval (subscribers, views, age)")
    print("✅ Rising Star Score calculation (0-100)")
    print("✅ Smart caching to minimize API calls")
    print("✅ Comprehensive error handling")
    print("✅ Rich UI with channel cards and scores")
    print("✅ Direct links to YouTube channels")
    print("✅ Performance metrics and API call tracking")
    print()
    
    print("🎯 Ready for testing with valid YouTube API key!")
    print("Set YOUTUBE_API_KEY environment variable for production use.")

if __name__ == "__main__":
    demo_rising_star_channels()