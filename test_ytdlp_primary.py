#!/usr/bin/env python3
"""
Test script for yt-dlp as PRIMARY data source
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ytdlp_basic():
    """Test basic yt-dlp data source functionality"""
    print("🧪 Testing YtDlpDataSource as PRIMARY data source...")
    
    try:
        from ytdlp_data_source import YtDlpDataSource
        from enhanced_ui_server import APICache
        
        # Create instances
        cache = APICache(ttl_seconds=3600)
        ytdlp_source = YtDlpDataSource(cache)
        
        print("✅ YtDlpDataSource imported successfully")
        
        # Test 1: Basic search
        print("\n1. Testing basic video search...")
        try:
            results = ytdlp_source.search("AI tutorial", max_results=3)
            if results and 'items' in results:
                print(f"✅ Search successful: Found {len(results['items'])} results")
                if results['items']:
                    first_item = results['items'][0]
                    print(f"   First result: {first_item.get('snippet', {}).get('title', 'No title')}")
                print(f"   Data source: {results.get('data_source', 'unknown')}")
            else:
                print("❌ Search failed: No results")
        except Exception as e:
            print(f"❌ Search failed with error: {e}")
        
        # Test 2: Channel search
        print("\n2. Testing channel search...")
        try:
            channel_results = ytdlp_source.search("programming", max_results=2, search_type='channel')
            if channel_results and 'items' in channel_results:
                print(f"✅ Channel search successful: Found {len(channel_results['items'])} channels")
                if channel_results['items']:
                    first_channel = channel_results['items'][0]
                    print(f"   First channel: {first_channel.get('snippet', {}).get('title', 'No title')}")
            else:
                print("❌ Channel search failed: No results")
        except Exception as e:
            print(f"❌ Channel search failed with error: {e}")
        
        # Test 3: Get channel info
        print("\n3. Testing channel info retrieval...")
        try:
            # Use a known channel ID (PewDiePie)
            channel_info = ytdlp_source.get_channel("UC-lHJZR3Gqxm24_Vd_AJ5Yw")
            if channel_info:
                print("✅ Channel info successful")
                print(f"   Channel: {channel_info.get('author', 'Unknown')}")
                print(f"   Subscribers: {channel_info.get('statistics', {}).get('subscriberCount', 'Unknown')}")
            else:
                print("❌ Channel info failed: No data")
        except Exception as e:
            print(f"❌ Channel info failed with error: {e}")
        
        # Test 4: Cache functionality
        print("\n4. Testing cache...")
        cache_stats = cache.get_stats()
        print(f"✅ Cache stats: {cache_stats}")
        
        print(f"\n📊 Total yt-dlp calls made: {ytdlp_source.call_count}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_server_integration():
    """Test integration with enhanced_ui_server"""
    print("\n🧪 Testing integration with enhanced_ui_server...")
    
    try:
        from enhanced_ui_server import get_shared_components
        
        # Get shared components
        cache, ytdlp_client, ytdlp_data_source, trends_api, niche_scorer, recommendation_engine, channel_discovery = get_shared_components()
        
        print("✅ Shared components initialized successfully")
        print(f"   Cache: {type(cache).__name__}")
        print(f"   YtDlp Data Source: {type(ytdlp_data_source).__name__}")
        print(f"   Trends API: {type(trends_api).__name__}")
        print(f"   Niche Scorer: {type(niche_scorer).__name__}")
        print(f"   Channel Discovery: {type(channel_discovery).__name__}")
        
        # Test channel discovery
        print("\n   Testing channel discovery...")
        try:
            rising_stars = channel_discovery.find_rising_star_channels("cooking", max_results=5)
            if rising_stars.get('success'):
                print(f"✅ Rising stars found: {len(rising_stars.get('channels', []))} channels")
                if rising_stars.get('channels'):
                    best = rising_stars['channels'][0]
                    print(f"   Best opportunity: {best.get('name', 'Unknown')}")
            else:
                print(f"❌ Rising stars failed: {rising_stars.get('analysis', {}).get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Channel discovery error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Server integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎯 Testing yt-dlp as PRIMARY Data Source")
    print("=" * 60)
    
    success1 = test_ytdlp_basic()
    success2 = test_server_integration()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests PASSED! yt-dlp is working as primary data source.")
    else:
        print("❌ Some tests FAILED. Check output above.")
    
    print("\n🚀 Next: Start the server with `python enhanced_ui_server.py`")
    return 0 if (success1 and success2) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)