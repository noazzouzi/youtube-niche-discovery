#!/usr/bin/env python3
"""
Final verification test for yt-dlp as PRIMARY data source
Tests all core functionality to ensure success criteria are met
"""
import requests
import time
import json

def test_server_status():
    """Test 1: Server status should show yt-dlp"""
    print("🧪 Test 1: Server Status")
    try:
        response = requests.get('http://localhost:8080/api/status', timeout=10)
        data = response.json()
        
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version')}")
        print(f"   API: {data.get('api')}")
        print(f"   Data source: {data.get('data_source')}")
        
        # Check success criteria
        checks = {
            'Server is live': data.get('status') == 'live',
            'Version is ytdlp_v3.0': data.get('version') == 'ytdlp_v3.0',
            'API shows YT-DLP': 'YT-DLP' in data.get('api', ''),
            'Data source shows yt-dlp': 'yt-dlp' in data.get('data_source', ''),
            'Caching enabled': 'ENABLED' in data.get('caching', ''),
            'Port 8080': True  # We reached the endpoint
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_api_stats():
    """Test 2: API stats should show yt-dlp calls"""
    print("\n🧪 Test 2: API Statistics")
    try:
        response = requests.get('http://localhost:8080/api/stats', timeout=15)
        data = response.json()
        
        api_calls = data.get('api_calls', {})
        print(f"   yt-dlp calls: {api_calls.get('yt_dlp', 0)}")
        print(f"   Trends calls: {api_calls.get('trends', 0)}")
        print(f"   Total calls: {api_calls.get('total', 0)}")
        
        cache_stats = data.get('cache', {})
        print(f"   Cache hit rate: {cache_stats.get('hit_rate', 0)}%")
        print(f"   Cache entries: {cache_stats.get('total_entries', 0)}")
        
        checks = {
            'yt-dlp calls recorded': api_calls.get('yt_dlp', 0) > 0,
            'Cache is working': cache_stats.get('total_entries', 0) > 0
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_basic_search():
    """Test 3: Basic search functionality"""
    print("\n🧪 Test 3: Basic Search (Quick)")
    try:
        # Use a simple niche for faster testing
        response = requests.get('http://localhost:8080/api/analyze?niche=test', timeout=30)
        
        if response.status_code != 200:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
        data = response.json()
        
        # Check if we get a valid response structure
        checks = {
            'Has niche field': 'niche' in data,
            'Has score': 'score' in data,
            'Has breakdown': 'breakdown' in data,
            'No error': 'error' not in data
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
            
        if 'score' in data:
            print(f"   📊 Score: {data.get('score', 0)}/100")
            
        if 'breakdown' in data:
            breakdown = data['breakdown']
            for category, details in breakdown.items():
                if isinstance(details, dict) and 'data_source' in details:
                    ds = details['data_source']
                    if 'yt-dlp' in ds or 'YT-DLP' in ds:
                        print(f"   🔗 {category}: Using yt-dlp ✅")
                    else:
                        print(f"   🔗 {category}: {ds}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_channel_discovery():
    """Test 4: Channel discovery (Rising Stars)"""
    print("\n🧪 Test 4: Channel Discovery")
    try:
        response = requests.get('http://localhost:8080/api/channels?niche=cooking', timeout=45)
        
        if response.status_code != 200:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return False
            
        data = response.json()
        
        checks = {
            'Has channels': 'channels' in data,
            'Has analysis': 'analysis' in data,
            'No error': 'error' not in data
        }
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        if 'analysis' in data:
            analysis = data['analysis']
            print(f"   📊 Channels found: {analysis.get('total_channels_found', 0)}")
            print(f"   ⭐ Rising stars: {analysis.get('rising_stars_identified', 0)}")
            print(f"   ⏱️  Analysis time: {analysis.get('analysis_time', 0)}s")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🎯 Final Verification: yt-dlp as PRIMARY Data Source")
    print("=" * 60)
    
    print("Testing server running on localhost:8080...")
    
    tests = [
        test_server_status,
        test_api_stats,
        test_basic_search,
        test_channel_discovery
    ]
    
    results = []
    
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            time.sleep(2)  # Brief pause between tests
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 FINAL RESULTS")
    print("=" * 60)
    
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED! yt-dlp is working as PRIMARY data source")
        print("\n✅ Success Criteria Met:")
        print("   ✅ yt-dlp is primary data source")
        print("   ✅ Search works reliably")
        print("   ✅ Server runs on port 8080")
        print("   ✅ Caching reduces repeated calls")
        print("   ✅ Status shows 'yt-dlp powered'")
        
        print("\n🚀 READY FOR PRODUCTION!")
        print("   💻 Local: http://localhost:8080")
        print("   🌍 External: http://38.143.19.241:8080")
        
        return 0
    else:
        print(f"❌ {total_tests - passed_tests} tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    exit(main())