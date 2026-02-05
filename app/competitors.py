"""
Competitor Analysis Module for YouTube Niche Discovery Engine

This module analyzes market saturation and competitor landscape in a niche
by examining active channels, their sizes, and market distribution.
"""

import time
import logging
from typing import Dict, Optional

from .cache import APICache

# Import the existing YtDlpDataSource from root level
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ytdlp_data_source import YtDlpDataSource
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("YtDlpDataSource not found! Make sure ytdlp_data_source.py is in the parent directory.")

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """Analyze market saturation and competitor landscape in a niche"""
    
    def __init__(self, ytdlp_data_source: YtDlpDataSource, cache: APICache):
        self.ytdlp_data_source = ytdlp_data_source
        self.cache = cache
        logger.info("CompetitorAnalyzer initialized")
    
    def analyze_competitors(self, niche: str, max_results: int = 30) -> dict:
        """Analyze competitor landscape for a given niche"""
        logger.info(f"Analyzing competitors for niche: {niche}")
        start_time = time.time()
        
        try:
            # Search for videos in this niche to identify channels
            videos = self.ytdlp_data_source.search(niche, max_results, search_type='video')
            if not videos or not videos.get('items'):
                return self._empty_competitor_response(niche, "No video search results found")
            
            # Aggregate channel data from video results
            channels = {}
            for video in videos['items']:
                # Extract channel info from video snippet
                snippet = video.get('snippet', {})
                channel_id = snippet.get('channelId')
                channel_name = snippet.get('channelTitle')
                
                if not channel_id or not channel_name:
                    continue
                
                if channel_id not in channels:
                    channels[channel_id] = {
                        'name': channel_name,
                        'id': channel_id,
                        'video_count': 0,
                        'total_views': 0,
                        'videos': []
                    }
                
                # Add video data
                statistics = video.get('statistics', {})
                view_count = int(statistics.get('viewCount', 0) or 0)
                channels[channel_id]['video_count'] += 1
                channels[channel_id]['total_views'] += view_count
                channels[channel_id]['videos'].append({
                    'title': snippet.get('title', ''),
                    'views': view_count,
                    'upload_date': snippet.get('publishedAt', '')
                })
            
            # Get detailed channel info for only the top channels (limit API calls)
            sorted_channels = sorted(
                channels.values(), 
                key=lambda x: x['total_views'], 
                reverse=True
            )
            
            competitor_channels = []
            total_unique_channels = len(channels)
            
            # For initial demonstration, get detailed info for just top 3 channels
            # This minimizes API calls as requested in the task
            for channel_data in sorted_channels[:3]:
                try:
                    channel_info = self.ytdlp_data_source.get_channel(channel_data['id'])
                    if channel_info:
                        statistics = channel_info.get('statistics', {})
                        subscriber_count = int(statistics.get('subscriberCount', 0) or 0)
                    else:
                        # Fallback: estimate based on view patterns
                        subscriber_count = self._estimate_subscribers_from_views(channel_data['total_views'], channel_data['video_count'])
                except Exception as e:
                    logger.warning(f"Could not get channel info for {channel_data['id']}: {e}")
                    # Use estimated subscriber count
                    subscriber_count = self._estimate_subscribers_from_views(channel_data['total_views'], channel_data['video_count'])
                
                avg_views = channel_data['total_views'] / max(channel_data['video_count'], 1)
                
                competitor_channels.append({
                    'name': channel_data['name'],
                    'id': channel_data['id'],
                    'subscribers': subscriber_count,
                    'video_count': channel_data['video_count'],
                    'avg_views': round(avg_views),
                    'total_views': channel_data['total_views'],
                    'subscriber_tier': self._get_subscriber_tier(subscriber_count)
                })
            
            # Calculate market saturation based on all unique channels found
            analysis = self._calculate_market_saturation(competitor_channels, total_unique_channels)
            
            # Get top competitors
            top_competitors = sorted(
                competitor_channels, 
                key=lambda x: x['subscribers'], 
                reverse=True
            )[:5]
            
            analysis_time = time.time() - start_time
            
            return {
                'niche': niche,
                'saturation_level': analysis['saturation_level'],
                'saturation_score': analysis['saturation_score'],
                'channel_count': total_unique_channels,
                'tier_breakdown': analysis['tier_breakdown'],
                'top_competitors': top_competitors,
                'performance': {
                    'analysis_time_seconds': round(analysis_time, 2),
                    'total_channels_analyzed': len(competitor_channels),
                    'ytdlp_calls': self.ytdlp_data_source.call_count
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis error for {niche}: {e}")
            return self._empty_competitor_response(niche, f"Error: {str(e)}")
    
    def _estimate_subscribers_from_views(self, total_views: int, video_count: int) -> int:
        """Estimate subscriber count based on video performance"""
        if video_count == 0:
            return 0
            
        avg_views = total_views / video_count
        
        # Rough estimation based on typical view-to-subscriber ratios
        # These are conservative estimates for demonstration
        if avg_views > 500000:
            return int(avg_views * 0.05)  # Large channels: ~5% of views = subscribers
        elif avg_views > 50000:
            return int(avg_views * 0.08)  # Medium channels: ~8% of views = subscribers
        elif avg_views > 5000:
            return int(avg_views * 0.12)  # Small channels: ~12% of views = subscribers
        else:
            return int(avg_views * 0.15)  # Micro channels: ~15% of views = subscribers
    
    def _get_subscriber_tier(self, subscriber_count: int) -> str:
        """Categorize channel by subscriber count"""
        if subscriber_count >= 100000:
            return 'large'
        elif subscriber_count >= 10000:
            return 'medium'
        elif subscriber_count >= 1000:
            return 'small'
        else:
            return 'micro'
    
    def _calculate_market_saturation(self, channels: list, total_unique_channels: int = None) -> dict:
        """Calculate market saturation metrics"""
        total_channels = total_unique_channels if total_unique_channels is not None else len(channels)
        
        # Count channels by tier
        tier_breakdown = {
            'micro': 0,    # 0-1K subscribers
            'small': 0,    # 1K-10K
            'medium': 0,   # 10K-100K  
            'large': 0     # 100K+
        }
        
        for channel in channels:
            tier = channel['subscriber_tier']
            tier_breakdown[tier] += 1
        
        # Calculate saturation level
        if total_channels < 10:
            saturation_level = 'low'
        elif total_channels < 50:
            saturation_level = 'medium'
        else:
            saturation_level = 'high'
        
        return {
            'saturation_level': saturation_level,
            'saturation_score': total_channels,
            'tier_breakdown': tier_breakdown
        }
    
    def _empty_competitor_response(self, niche: str, reason: str) -> dict:
        """Return empty competitor analysis response"""
        return {
            'niche': niche,
            'saturation_level': 'unknown',
            'saturation_score': 0,
            'channel_count': 0,
            'tier_breakdown': {'micro': 0, 'small': 0, 'medium': 0, 'large': 0},
            'top_competitors': [],
            'error_reason': reason,
            'success': False
        }