#!/usr/bin/env python3
"""
Test script for yt-dlp integration
"""
import sys
import os
import json

# Add the current directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_ui_server import APICache, YtDlpClient, InvidiousAPI

def test_ytdlp_basic():
    """Test basic yt-dlp functionality"""
    print("🧪 Testing yt-dlp basic functionality...")
    
    # Create cache and client
    cache = APICache(ttl_seconds=7200)
    ytdlp_client = YtDlpClient(cache)
    
    # Test 1: Search functionality
    print("\n1. Testing video search...")
    try:
        results = ytdlp_client.search_videos("AI tutorial", max_results=3)
        if results:
            print(f"✅ Search successful: Found {len(results)} videos")
            print(f"   First result: {results[0].get('title', 'No title')}")
        else:
            print("❌ Search failed: No results")
    except Exception as e:
        print(f"❌ Search failed with error: {e}")
    
    # Test 2: Video info extraction
    print("\n2. Testing video info extraction...")
    test_video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    try:
        video_info = ytdlp_client.get_video_info(test_video_url)
        if video_info:
            print(f"✅ Video info successful")
            print(f"   Title: {video_info.get('title', 'No title')}")
            print(f"   View count: {video_info.get('view_count', 'Unknown')}")
            print(f"   Channel: {video_info.get('uploader', 'Unknown')}")
        else:
            print("❌ Video info failed: No data")
    except Exception as e:
        print(f"❌ Video info failed with error: {e}")
    
    # Test 3: Cache functionality
    print("\n3. Testing cache...")
    cache_stats = cache.get_stats()
    print(f"✅ Cache stats: {cache_stats}")
    
    print(f"\n📊 yt-dlp API calls made: {ytdlp_client.call_count}")

def test_invidious_ytdlp_fallback():
    """Test Invidious + yt-dlp fallback integration"""
    print("\n🧪 Testing Invidious + yt-dlp fallback integration...")
    
    # Create components
    cache = APICache(ttl_seconds=7200)
    ytdlp_client = YtDlpClient(cache)
    invidious_api = InvidiousAPI(cache, ytdlp_client)
    
    # Test fallback scenario - try to get info for a channel
    print("\n1. Testing channel info with fallback...")
    test_channel_id = "UC-lHJZR3Gqxm24_Vd_AJ5Yw"  # PewDiePie
    try:
        channel_info = invidious_api.get_channel(test_channel_id)
        if channel_info:
            print(f"✅ Channel info successful")
            print(f"   Channel: {channel_info.get('author', 'Unknown')}")
            print(f"   Subscribers: {channel_info.get('subCount', 'Unknown')}")
            data_source = channel_info.get('data_source', 'invidious')
            print(f"   Data source: {data_source}")
        else:
            print("❌ Channel info failed")
    except Exception as e:
        print(f"❌ Channel info failed with error: {e}")
    
    print(f"\n📊 API call counts:")
    print(f"   Invidious: {invidious_api.call_count}")
    print(f"   yt-dlp: {ytdlp_client.call_count}")

def main():
    """Run all tests"""
    print("🎯 Testing yt-dlp Integration for YouTube Niche Discovery")
    print("=" * 60)
    
    try:
        test_ytdlp_basic()
        test_invidious_ytdlp_fallback()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed! Check output above for results.")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)