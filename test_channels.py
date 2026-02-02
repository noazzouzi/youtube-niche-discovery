#!/usr/bin/env python3
"""Test the Rising Star Channels feature"""

import sys
import os

# Add the directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_server import get_shared_components

def test_channel_discovery():
    """Test the channel discovery functionality"""
    print("🧪 Testing Rising Star Channels Discovery...")
    
    try:
        # Get the shared components
        cache, youtube_api, trends_api, niche_scorer, recommendation_engine, channel_discovery = get_shared_components()
        
        print(f"✅ Components initialized successfully")
        print(f"🔑 YouTube API Key: ...{youtube_api.api_key[-4:]}")
        
        # Test with a simple niche
        test_niche = "ai tutorial"
        print(f"🎯 Testing with niche: '{test_niche}'")
        
        # Discover rising star channels
        result = channel_discovery.find_rising_star_channels(test_niche, max_results=5)
        
        print(f"\n📊 Results:")
        print(f"Success: {result['success']}")
        print(f"Niche: {result['niche']}")
        print(f"Channels found: {result['analysis']['total_channels_found']}")
        print(f"Rising stars identified: {result['analysis']['rising_stars_identified']}")
        
        if result['success'] and result['channels']:
            print(f"\n🌟 Top Rising Star Channels:")
            for i, channel in enumerate(result['channels'][:3], 1):
                print(f"{i}. {channel['name']}")
                print(f"   Score: {channel['rising_star_score']}")
                print(f"   Subscribers: {channel['subscribers']:,}")
                print(f"   Views/Sub: {channel['views_per_subscriber']}")
                print(f"   Age: {channel['channel_age']}")
                print(f"   Why: {channel['why_rising_star']}")
                print(f"   URL: {channel['url']}")
                print()
        elif not result['success']:
            print(f"❌ Error: {result['analysis'].get('error_reason', 'Unknown error')}")
        else:
            print("ℹ️  No rising star channels found")
        
        print(f"\n⚡ API Statistics:")
        print(f"YouTube API calls: {youtube_api.call_count}")
        print(f"Cache entries: {len(cache.cache)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_channel_discovery()
    if result and result['success']:
        print("\n✅ Test completed successfully!")
        
        # Also test the new endpoint response format
        print("\n📝 Sample API Response:")
        import json
        print(json.dumps(result, indent=2)[:1000] + "...")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)