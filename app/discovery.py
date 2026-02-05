"""
Channel Discovery Module for YouTube Niche Discovery Engine

This module discovers and scores Rising Star channels in a niche using
optimized video metadata approach and content type analysis.
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .cache import APICache

# Import the existing modules from root level
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ytdlp_data_source import YtDlpDataSource, ContentTypeAnalyzer
except ImportError:
    logger = logging.getLogger(__name__)
    logger.error("YtDlpDataSource/ContentTypeAnalyzer not found! Make sure ytdlp_data_source.py is in the parent directory.")

logger = logging.getLogger(__name__)


class ChannelDiscovery:
    """Discover and score Rising Star channels in a niche"""
    
    def __init__(self, ytdlp_data_source: YtDlpDataSource, cache: APICache):
        self.ytdlp_data_source = ytdlp_data_source
        self.cache = cache
        logger.info("ChannelDiscovery initialized")
    
    def find_rising_star_channels(self, niche: str, max_results: int = 50) -> dict:
        """Find rising star channels in a niche using optimized video metadata approach"""
        logger.info(f"Finding rising star channels for: {niche} (OPTIMIZED)")
        start_time = time.time()
        
        try:
            # Step 1: Search for videos (this already gets channel data!)
            videos = self.ytdlp_data_source.search(niche, max_results, search_type='video')
            if not videos or not videos.get('items'):
                return self._empty_response(niche, "No video search results found")
            
            # Step 2: Aggregate channel stats from video results  
            channels = {}
            for video in videos['items']:
                if video.get('id', {}).get('kind') != 'youtube#video':
                    continue
                    
                snippet = video.get('snippet', {})
                ch_id = snippet.get('channelId')
                if not ch_id:
                    continue
                    
                if ch_id not in channels:
                    # Use @ handle URL if available, otherwise fall back to channel ID
                    channel_url = snippet.get('channelUrl', f"https://www.youtube.com/channel/{ch_id}")
                    channels[ch_id] = {
                        'name': snippet.get('channelTitle', 'Unknown'),
                        'channel_id': ch_id,
                        'subscribers': 0,  # Will be estimated from video metadata
                        'total_views': 0,
                        'video_count': 0,
                        'latest_upload': None,
                        'url': channel_url,
                        'videos': []
                    }
                
                # Aggregate stats (note: individual video views not available in search)
                channels[ch_id]['video_count'] += 1
                channels[ch_id]['videos'].append(video)
                
                # Track latest upload
                published_at = snippet.get('publishedAt')
                if published_at:
                    if not channels[ch_id]['latest_upload'] or published_at > channels[ch_id]['latest_upload']:
                        channels[ch_id]['latest_upload'] = published_at
            
            # Step 3: Get detailed video info for top channels to extract subscriber counts
            # Sort by video count first to prioritize active channels
            channel_list = list(channels.values())
            channel_list.sort(key=lambda x: x['video_count'], reverse=True)
            
            # Get detailed info for top 10 channels to extract subscriber data
            for i, channel_data in enumerate(channel_list[:10]):
                try:
                    # Get one video's detailed metadata to extract channel follower count
                    first_video = channel_data['videos'][0]
                    video_id = first_video.get('id', {}).get('videoId')
                    if video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        video_info = self.ytdlp_data_source.get_video_info(video_url, use_cache=True)
                        if video_info:
                            # Extract subscriber count from video metadata
                            channel_data['subscribers'] = video_info.get('channel_follower_count', 0)
                            # Estimate total views based on channel data
                            if video_info.get('view_count'):
                                # Rough estimate: multiply by video count
                                avg_views = video_info.get('view_count', 0)
                                channel_data['total_views'] = avg_views * channel_data['video_count']
                    
                    # Small delay to be nice
                    if i < 9:
                        time.sleep(0.2)
                        
                except Exception as e:
                    logger.warning(f"Error getting video details for channel {channel_data['channel_id']}: {e}")
                    # Set fallback values
                    channel_data['subscribers'] = 0
                    channel_data['total_views'] = 0
            
            # Step 3.5: Analyze content types for faceless content detection
            content_type_analyzer = ContentTypeAnalyzer()
            for ch_id, ch_data in channels.items():
                try:
                    # Prepare channel data for content type analysis
                    analysis_data = {
                        'snippet': {
                            'title': ch_data.get('name', ''),
                            'description': ''  # We don't have channel description in this context
                        },
                        'videos': ch_data.get('videos', [])
                    }
                    
                    # Analyze content type
                    content_analysis = content_type_analyzer.analyze_channel(analysis_data)
                    ch_data.update({
                        'content_type': content_analysis['content_type'],
                        'faceless_score': content_analysis['faceless_score'],
                        'copy_indicators': content_analysis['copy_indicators'],
                        'avg_duration_minutes': content_analysis.get('avg_duration_minutes', 0),
                        'has_long_videos': content_analysis.get('has_long_videos', False)
                    })
                    
                    logger.debug(f"Content analysis for {ch_data['name']}: {content_analysis['content_type']} (score: {content_analysis['faceless_score']})")
                
                except Exception as e:
                    logger.warning(f"Error analyzing content type for channel {ch_id}: {e}")
                    # Set fallback values
                    ch_data.update({
                        'content_type': 'unknown',
                        'faceless_score': 0,
                        'copy_indicators': [],
                        'avg_duration_minutes': 0,
                        'has_long_videos': False
                    })
            
            # Step 4: Calculate rising star scores  
            rising_stars = []
            for ch_id, ch_data in channels.items():
                try:
                    # FILTER: Only include channels with 20+ min average videos
                    if not ch_data.get('has_long_videos', False):
                        logger.debug(f"Skipping {ch_data.get('name', 'unknown')} - avg duration < 20 min")
                        continue
                    
                    score = self._calculate_rising_star_score_from_aggregated_data(ch_data)
                    ch_data['rising_star_score'] = score
                    if score >= 50:  # Minimum threshold
                        rising_stars.append(ch_data)
                except Exception as e:
                    logger.warning(f"Error scoring channel {ch_id}: {e}")
                    continue
            
            # Step 5: Sort and return top channels
            rising_stars.sort(key=lambda x: x['rising_star_score'], reverse=True)
            top_rising_stars = rising_stars[:10]
            
            analysis_time = time.time() - start_time
            
            return {
                'niche': niche,
                'channels': top_rising_stars,
                'analysis': {
                    'total_channels_found': len(channels),
                    'rising_stars_identified': len(top_rising_stars),
                    'best_opportunity': top_rising_stars[0]['name'] if top_rising_stars else None,
                    'analysis_time': round(analysis_time, 2),
                    'optimization': 'ENABLED - Using video metadata aggregation'
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Channel discovery error for {niche}: {e}")
            return self._empty_response(niche, f"Error: {str(e)}")
    
    def _calculate_rising_star_score_from_aggregated_data(self, channel: dict) -> float:
        """Calculate rising star score for aggregated channel data"""
        subscribers = channel.get('subscribers', 0)
        total_views = channel.get('total_views', 0)
        video_count = channel.get('video_count', 0)
        
        # Views per subscriber (viral potential) - max 40 points
        if subscribers > 0:
            views_per_sub = total_views / subscribers
            viral_score = min(views_per_sub / 10, 40)  # Max 40 pts
        else:
            viral_score = 20  # Unknown subs, moderate score
        
        # Low subscriber bonus (opportunity) - max 30 points
        if subscribers == 0:
            size_score = 25  # Unknown, give benefit of doubt
        elif subscribers < 10000:
            size_score = 30
        elif subscribers < 50000:
            size_score = 25
        elif subscribers < 100000:
            size_score = 20
        else:
            size_score = 10
        
        # Activity score (based on videos in search results) - max 30 points
        if video_count >= 5:
            activity_score = 30
        elif video_count >= 3:
            activity_score = 25
        elif video_count >= 2:
            activity_score = 20
        else:
            activity_score = 15
        
        return viral_score + size_score + activity_score
    
    def _empty_response(self, niche: str, reason: str) -> dict:
        """Return empty response structure"""
        return {
            'niche': niche,
            'channels': [],
            'analysis': {
                'total_channels_found': 0,
                'rising_stars_identified': 0,
                'best_opportunity': None,
                'error_reason': reason
            },
            'success': False
        }