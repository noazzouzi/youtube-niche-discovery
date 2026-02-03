#!/usr/bin/env python3
"""Test the Rising Star Channels feature with mock data"""

import sys
import os
from datetime import datetime, timedelta

# Add the directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rising_star_scoring():
    """Test the rising star scoring algorithm with mock data"""
    print("🧪 Testing Rising Star Scoring Algorithm...")
    
    # Import after path setup
    from enhanced_ui_server import ChannelDiscovery, APICache, YouTubeAPI
    
    # Create mock instances
    cache = APICache()
    youtube_api = YouTubeAPI("test_key", cache)
    channel_discovery = ChannelDiscovery(youtube_api, cache)
    
    # Mock channel data representing different types of channels
    mock_channels = [
        {
            # Rising star: small channel, high engagement, relatively new
            'id': 'UC123',
            'snippet': {
                'title': 'AI Explained Simply',
                'description': 'Making AI easy to understand',
                'publishedAt': '2023-06-15T10:00:00Z'  # ~8 months old
            },
            'statistics': {
                'subscriberCount': '8500',
                'viewCount': '1200000',
                'videoCount': '45'
            }
        },
        {
            # Established channel: large subscriber base, lower views/sub ratio
            'id': 'UC456',
            'snippet': {
                'title': 'Tech Giant Channel',
                'description': 'Established tech channel',
                'publishedAt': '2019-01-15T10:00:00Z'  # 5 years old
            },
            'statistics': {
                'subscriberCount': '500000',
                'viewCount': '25000000',
                'videoCount': '200'
            }
        },
        {
            # High potential: very new, small but viral content
            'id': 'UC789',
            'snippet': {
                'title': 'AI Breakthrough News',
                'description': 'Latest AI developments',
                'publishedAt': '2024-01-15T10:00:00Z'  # ~1 year old
            },
            'statistics': {
                'subscriberCount': '2500',
                'viewCount': '800000',
                'videoCount': '25'
            }
        },
        {
            # Moderate opportunity: medium-sized, decent growth
            'id': 'UC012',
            'snippet': {
                'title': 'AI Learning Hub',
                'description': 'AI tutorials and guides',
                'publishedAt': '2022-08-15T10:00:00Z'  # ~1.5 years old
            },
            'statistics': {
                'subscriberCount': '45000',
                'viewCount': '3200000',
                'videoCount': '80'
            }
        }
    ]
    
    print("📊 Testing scoring algorithm on mock channels:\n")
    
    scored_channels = []
    
    for channel_data in mock_channels:
        try:
            # Calculate rising star score
            result = channel_discovery._calculate_rising_star_score(channel_data)
            scored_channels.append(result)
            
            # Display results
            print(f"🎯 {result['name']}")
            print(f"   Score: {result['rising_star_score']}/100")
            print(f"   Subscribers: {result['subscribers']:,}")
            print(f"   Views/Sub: {result['views_per_subscriber']}")
            print(f"   Age: {result['channel_age']}")
            print(f"   Why Rising Star: {result['why_rising_star']}")
            print(f"   Score Breakdown:")
            print(f"     - Viral Potential: {result['score_breakdown']['viral_potential']}/40")
            print(f"     - Opportunity Size: {result['score_breakdown']['opportunity_size']}/30") 
            print(f"     - Age Factor: {result['score_breakdown']['age_factor']}/30")
            print()
            
        except Exception as e:
            print(f"❌ Error processing {channel_data['snippet']['title']}: {e}")
    
    # Sort by score to show ranking
    scored_channels.sort(key=lambda x: x['rising_star_score'], reverse=True)
    
    print("🏆 Rising Star Rankings:")
    for i, channel in enumerate(scored_channels, 1):
        indicator = "🔥" if channel['rising_star_score'] >= 80 else "⭐" if channel['rising_star_score'] >= 70 else "👍"
        print(f"{i}. {indicator} {channel['name']} - Score: {channel['rising_star_score']}")
    
    # Test the response format  
    mock_response = {
        'niche': 'ai tutorial',
        'channels': scored_channels,
        'analysis': {
            'total_channels_found': len(scored_channels),
            'rising_stars_identified': len([c for c in scored_channels if c['rising_star_score'] >= 50]),
            'best_opportunity': scored_channels[0]['name'] if scored_channels else None,
            'analysis_time': 0.5
        },
        'success': True
    }
    
    print(f"\n📝 Sample API Response Structure:")
    import json
    print(json.dumps(mock_response, indent=2)[:800] + "..." if len(json.dumps(mock_response, indent=2)) > 800 else json.dumps(mock_response, indent=2))
    
    return mock_response

if __name__ == "__main__":
    try:
        result = test_rising_star_scoring()
        print("\n✅ Rising Star scoring algorithm test completed successfully!")
        
        # Validate scoring logic
        scores = [ch['rising_star_score'] for ch in result['channels']]
        print(f"\nScore range: {min(scores):.1f} - {max(scores):.1f}")
        print(f"High potential channels (70+ score): {len([s for s in scores if s >= 70])}")
        print(f"Algorithm working correctly: {'✅' if max(scores) > 70 and min(scores) < max(scores) else '❌'}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)