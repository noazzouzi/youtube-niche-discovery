"""
YouTube API Module for YouTube Niche Discovery Engine

This module provides a YouTube API client using yt-dlp as the data source,
with caching support and compatibility with YouTube API format.
"""

import logging
from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING

from .cache import APICache
from .ytdlp_client import YtDlpClient

# Import the existing YtDlpDataSource from root level
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from ytdlp_data_source import YtDlpDataSource
except ImportError:
    logger.error("YtDlpDataSource not found! Make sure ytdlp_data_source.py is in the parent directory.")
    sys.exit(1)

logger = logging.getLogger(__name__)


class YouTubeAPI:
    """YouTube API client using yt-dlp, with caching support"""
    
    def __init__(self, cache: APICache, ytdlp_client: Optional[YtDlpClient] = None):
        self.cache = cache
        self.ytdlp_client = ytdlp_client
        self.call_count = 0
        logger.info(f"YouTubeAPI initialized with yt-dlp data source")
    
    def _use_ytdlp_fallback(self) -> bool:
        """Check if yt-dlp fallback should be used (always true now)"""
        return self.ytdlp_client is not None
    
    def search(self, query: str, max_results: int = 30, search_type: str = 'all', use_cache: bool = True) -> Optional[dict]:
        """Search YouTube with caching support"""
        cache_key = self.cache._generate_key('youtube_search', {
            'query': query,
            'max_results': max_results,
            'type': search_type
        })
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached YouTube search for: {query}")
                return cached_result
        
        # Use yt-dlp for search
        result = None
        if self._use_ytdlp_fallback():
            try:
                if search_type == 'channel':
                    # For channel search, use yt-dlp to search for channels
                    ytdlp_result = self.ytdlp_client.search_channels(query, max_results)
                else:
                    # For video search, use yt-dlp
                    ytdlp_result = self.ytdlp_client.search_videos(query, max_results)
                
                if ytdlp_result:
                    result = self._convert_search_response(ytdlp_result, max_results)
                    self.call_count += 1
                    logger.debug(f"YouTube search via yt-dlp successful: {query}")
                
            except Exception as e:
                logger.error(f"yt-dlp search failed for query '{query}': {e}")
                return None
        else:
            logger.error("No yt-dlp client available for search")
            return None
        
        if result and use_cache:
            self.cache.set(cache_key, result)
        
        return result
    
    def get_channel(self, channel_id: str, use_cache: bool = True) -> Optional[dict]:
        """Get channel information using yt-dlp"""
        cache_key = self.cache._generate_key('youtube_channel', {'channel_id': channel_id})
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached channel data for: {channel_id}")
                return cached_result
        
        result = None
        if self._use_ytdlp_fallback():
            try:
                ytdlp_result = self.ytdlp_client.get_channel_info(channel_id)
                if ytdlp_result:
                    result = self._convert_ytdlp_channel_to_youtube_format(ytdlp_result, channel_id)
                    self.call_count += 1
                    logger.debug(f"Channel info via yt-dlp successful: {channel_id}")
            except Exception as e:
                logger.error(f"yt-dlp channel lookup failed for {channel_id}: {e}")
        
        if result and use_cache:
            self.cache.set(cache_key, result)
        
        return result
    
    def _convert_ytdlp_channel_to_youtube_format(self, ytdlp_data: dict, channel_id: str) -> dict:
        """Convert yt-dlp channel data to YouTube API compatible format"""
        try:
            return {
                'authorId': channel_id,
                'author': ytdlp_data.get('channel_title', 'Unknown Channel'),
                'subCount': ytdlp_data.get('channel_follower_count', 0),
                'videoCount': len(ytdlp_data.get('videos', [])),
                'description': f"Channel data enhanced via yt-dlp",
                'authorUrl': ytdlp_data.get('channel_url') or f'https://www.youtube.com/channel/{channel_id}',
                'videos': ytdlp_data.get('videos', [])[:10],  # Limit to 10 recent videos
                'data_source': 'yt-dlp_enhanced'
            }
        except Exception as e:
            logger.error(f"Error converting yt-dlp data: {e}")
            return {
                'authorId': channel_id,
                'author': 'Unknown Channel',
                'subCount': 0,
                'videoCount': 0,
                'data_source': 'yt-dlp_fallback_error'
            }
    
    def get_channel_videos(self, channel_id: str, use_cache: bool = True) -> Optional[dict]:
        """Get channel videos using yt-dlp"""
        cache_key = self.cache._generate_key('youtube_channel_videos', {'channel_id': channel_id})
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached channel videos for: {channel_id}")
                return cached_result
        
        result = None
        if self._use_ytdlp_fallback():
            try:
                ytdlp_result = self.ytdlp_client.get_channel_videos(channel_id)
                if ytdlp_result:
                    result = ytdlp_result
                    self.call_count += 1
                    logger.debug(f"Channel videos via yt-dlp successful: {channel_id}")
            except Exception as e:
                logger.error(f"yt-dlp channel videos failed for {channel_id}: {e}")
        
        if result and use_cache:
            self.cache.set(cache_key, result)
        
        return result
    
    def _convert_search_response(self, ytdlp_result: list, max_results: int) -> dict:
        """Convert yt-dlp search response to YouTube API format"""
        if not isinstance(ytdlp_result, list):
            return {'items': [], 'pageInfo': {'totalResults': 0}}
        
        items = []
        for item in ytdlp_result[:max_results]:
            try:
                if item.get('type') == 'video':
                    # Convert video item
                    youtube_item = {
                        'kind': 'youtube#searchResult',
                        'id': {
                            'kind': 'youtube#video',
                            'videoId': item.get('videoId', '')
                        },
                        'snippet': {
                            'title': item.get('title', ''),
                            'description': item.get('description', '')[:200],  # Truncate description
                            'channelId': item.get('authorId', ''),
                            'channelTitle': item.get('author', ''),
                            'publishedAt': self._convert_timestamp(item.get('published', 0)),
                            'thumbnails': {
                                'default': {'url': item.get('videoThumbnails', [{}])[0].get('url', '')}
                            }
                        }
                    }
                    items.append(youtube_item)
                
                elif item.get('type') == 'channel':
                    # Convert channel item
                    youtube_item = {
                        'kind': 'youtube#searchResult',
                        'id': {
                            'kind': 'youtube#channel',
                            'channelId': item.get('authorId', '')
                        },
                        'snippet': {
                            'title': item.get('author', ''),
                            'description': item.get('description', '')[:200],
                            'channelId': item.get('authorId', ''),
                            'channelTitle': item.get('author', ''),
                            'thumbnails': {
                                'default': {'url': item.get('authorThumbnails', [{}])[-1].get('url', '') if item.get('authorThumbnails') else ''}
                            }
                        }
                    }
                    items.append(youtube_item)
                    
            except Exception as e:
                logger.warning(f"Error converting search item: {e}")
                continue
        
        return {
            'kind': 'youtube#searchListResponse',
            'items': items,
            'pageInfo': {
                'totalResults': len(items) * 100,  # Estimate total results
                'resultsPerPage': len(items)
            }
        }
    
    def _convert_timestamp(self, timestamp: int) -> str:
        """Convert Unix timestamp to ISO format"""
        if not timestamp:
            return datetime.now().isoformat() + 'Z'
        
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.isoformat() + 'Z'
        except:
            return datetime.now().isoformat() + 'Z'