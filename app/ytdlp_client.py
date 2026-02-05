"""
yt-dlp Client Module for YouTube Niche Discovery Engine

This module provides enhanced video/channel metadata extraction using yt-dlp.
It handles video info, channel info, and search functionality with caching support.
"""

import json
import subprocess
import logging
from typing import Optional, List

from .cache import APICache

logger = logging.getLogger(__name__)


class YtDlpClient:
    """yt-dlp client for enhanced video/channel metadata extraction"""
    
    def __init__(self, cache: APICache):
        self.cache = cache
        self.timeout = 30
        self.call_count = 0
        logger.info("YtDlpClient initialized")
    
    def get_video_info(self, video_url: str, use_cache: bool = True) -> Optional[dict]:
        """Get detailed video metadata using yt-dlp"""
        cache_key = self.cache._generate_key('ytdlp_video', {'url': video_url})
        
        # Try cache first  
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached yt-dlp video data for: {video_url}")
                return cached_result
        
        try:
            logger.info(f"Getting video info via yt-dlp: {video_url}")
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--no-playlist',
                video_url
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                check=True
            )
            
            self.call_count += 1
            video_data = json.loads(result.stdout)
            
            # Cache with 2-hour TTL
            if use_cache:
                temp_cache = APICache(ttl_seconds=7200)
                temp_cache.cache = self.cache.cache
                temp_cache.set(cache_key, video_data)
            
            return video_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp timeout for video: {video_url}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp error for video {video_url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"yt-dlp JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp unexpected error: {e}")
            return None
    
    def get_channel_info(self, channel_url: str, use_cache: bool = True) -> Optional[dict]:
        """Get channel metadata using yt-dlp"""
        cache_key = self.cache._generate_key('ytdlp_channel', {'url': channel_url})
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached yt-dlp channel data for: {channel_url}")
                return cached_result
        
        try:
            logger.info(f"Getting channel info via yt-dlp: {channel_url}")
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--playlist-items', '1:5',  # First 5 videos for metadata
                channel_url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True, 
                timeout=self.timeout,
                check=True
            )
            
            self.call_count += 1
            
            # Parse multiple JSON objects (one per video)
            lines = result.stdout.strip().split('\n')
            videos = []
            channel_data = {}
            
            for line in lines:
                if line.strip():
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                        
                        # Extract channel info from first video
                        if not channel_data and video_data:
                            channel_data = {
                                'channel_id': video_data.get('channel_id', ''),
                                'channel_title': video_data.get('uploader', ''),
                                'channel_follower_count': video_data.get('channel_follower_count', 0),
                                'channel_url': video_data.get('uploader_url', ''),
                                'videos': videos[:5]  # Limit to 5 videos
                            }
                    except json.JSONDecodeError:
                        continue
            
            if channel_data:
                # Cache with 4-hour TTL
                if use_cache:
                    temp_cache = APICache(ttl_seconds=14400)
                    temp_cache.cache = self.cache.cache
                    temp_cache.set(cache_key, channel_data)
                
                return channel_data
            else:
                logger.warning(f"No valid channel data extracted from: {channel_url}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp timeout for channel: {channel_url}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp error for channel {channel_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp unexpected error for channel: {e}")
            return None
    
    def search_videos(self, query: str, max_results: int = 10, use_cache: bool = True) -> Optional[List[dict]]:
        """Search YouTube via yt-dlp"""
        cache_key = self.cache._generate_key('ytdlp_search', {
            'query': query,
            'max_results': max_results
        })
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached yt-dlp search for: {query}")
                return cached_result
        
        try:
            logger.info(f"Searching via yt-dlp: {query}")
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--no-download',
                '--flat-playlist',
                f'ytsearch{max_results}:{query}'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True
            )
            
            self.call_count += 1
            
            # Parse search results
            lines = result.stdout.strip().split('\n')
            videos = []
            
            for line in lines:
                if line.strip():
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                    except json.JSONDecodeError:
                        continue
            
            # Cache with 2-hour TTL
            if use_cache:
                temp_cache = APICache(ttl_seconds=7200)
                temp_cache.cache = self.cache.cache
                temp_cache.set(cache_key, videos)
            
            return videos
            
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp search timeout for: {query}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp search error for {query}: {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp search unexpected error: {e}")
            return None
    
    def get_channel_stats_by_id(self, channel_id: str, use_cache: bool = True) -> Optional[dict]:
        """Get detailed channel stats by channel ID using yt-dlp"""
        if not channel_id:
            return None
        
        # Convert channel ID to URL
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        return self.get_channel_info(channel_url, use_cache)