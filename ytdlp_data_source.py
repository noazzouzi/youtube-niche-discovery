#!/usr/bin/env python3
"""
YtDlp Data Source - Primary YouTube data source using yt-dlp
Replaces Invidious API as the main data provider for YouTube Niche Discovery
"""

import subprocess
import json
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class YtDlpDataSource:
    """Primary YouTube data source using yt-dlp directly"""
    
    def __init__(self, cache):
        self.cache = cache
        self.timeout = 30
        self.call_count = 0
        logger.info("YtDlpDataSource initialized as PRIMARY data source")
    
    def search(self, query: str, max_results: int = 20, search_type: str = 'all', use_cache: bool = True) -> Optional[dict]:
        """Search YouTube using yt-dlp - primary search method"""
        cache_key = self.cache._generate_key('ytdlp_search', {
            'query': query,
            'max_results': max_results,
            'type': search_type
        })
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached yt-dlp search for: {query}")
                return cached_result
        
        try:
            logger.info(f"Searching YouTube via yt-dlp: {query} (max: {max_results})")
            
            if search_type == 'channel':
                # Search specifically for channels
                search_query = f"ytsearch{max_results}:{query} channel"
            else:
                # Default video search
                search_query = f"ytsearch{max_results}:{query}"
            
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--flat-playlist',
                '--no-download',
                search_query
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                check=True
            )
            
            self.call_count += 1
            
            # Parse JSON lines
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                    except json.JSONDecodeError:
                        continue
            
            # Convert to YouTube API format
            youtube_format = self._convert_search_response(videos, max_results, search_type)
            
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, youtube_format)
            
            logger.info(f"yt-dlp search successful: {len(videos)} results for '{query}'")
            return youtube_format
            
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp search timeout for: {query}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp search error for '{query}': {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp search unexpected error: {e}")
            return None
    
    def get_channel(self, channel_id: str, use_cache: bool = True) -> Optional[dict]:
        """Get detailed channel information using yt-dlp"""
        cache_key = self.cache._generate_key('ytdlp_channel', {'channel_id': channel_id})
        
        # Try cache first
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Using cached yt-dlp channel data for: {channel_id}")
                return cached_result
        
        try:
            logger.info(f"Getting channel info via yt-dlp: {channel_id}")
            
            # Handle different channel ID formats
            if channel_id.startswith('@'):
                # Channel handle format
                channel_url = f"https://www.youtube.com/{channel_id}"
            elif channel_id.startswith('UC'):
                # Standard channel ID format
                channel_url = f"https://www.youtube.com/channel/{channel_id}"
            else:
                # Assume it's a handle without @
                channel_url = f"https://www.youtube.com/@{channel_id}"
            
            # Get channel info by fetching first few videos
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
            
            # Parse video data to extract channel info
            videos = []
            channel_data = None
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_data = json.loads(line)
                        videos.append(video_data)
                        
                        # Extract channel data from first video
                        if not channel_data:
                            channel_data = self._extract_channel_from_video(video_data, channel_id)
                    except json.JSONDecodeError:
                        continue
            
            if channel_data:
                # Cache the result
                if use_cache:
                    self.cache.set(cache_key, channel_data)
                
                logger.info(f"yt-dlp channel data successful for: {channel_id}")
                return channel_data
            else:
                logger.warning(f"No channel data extracted for: {channel_id}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp channel timeout for: {channel_id}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp channel error for '{channel_id}': {e}")
            logger.debug(f"yt-dlp stderr: {e.stderr if hasattr(e, 'stderr') else 'No stderr'}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp channel unexpected error: {e}")
            return None
    
    def get_video_info(self, video_url: str, use_cache: bool = True) -> Optional[dict]:
        """Get detailed video information using yt-dlp"""
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
            
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, video_data)
            
            logger.info(f"yt-dlp video info successful")
            return video_data
            
        except subprocess.TimeoutExpired:
            logger.error(f"yt-dlp video timeout for: {video_url}")
            return None
        except subprocess.CalledProcessError as e:
            logger.error(f"yt-dlp video error for '{video_url}': {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"yt-dlp video JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"yt-dlp video unexpected error: {e}")
            return None
    
    def search_videos(self, query: str, max_results: int = 10, use_cache: bool = True) -> Optional[List[dict]]:
        """Search for videos and return raw yt-dlp data"""
        result = self.search(query, max_results, 'video', use_cache)
        if result and 'items' in result:
            # Extract video data from YouTube API format
            videos = []
            for item in result['items']:
                if item.get('id', {}).get('kind') == 'youtube#video':
                    videos.append(item)
            return videos
        return None
    
    def find_rising_stars(self, niche: str, max_results: int = 50) -> dict:
        """Find rising star channels in a niche using yt-dlp"""
        logger.info(f"Finding rising stars via yt-dlp for niche: {niche}")
        
        try:
            # Search for videos in the niche
            search_results = self.search(niche, max_results, 'video')
            if not search_results or not search_results.get('items'):
                return {'channels': [], 'total': 0, 'error': 'No search results'}
            
            # Group by channel and calculate metrics
            channel_stats = {}
            
            for item in search_results['items']:
                if item.get('id', {}).get('kind') != 'youtube#video':
                    continue
                    
                snippet = item.get('snippet', {})
                channel_id = snippet.get('channelId')
                channel_title = snippet.get('channelTitle')
                
                if channel_id and channel_title:
                    if channel_id not in channel_stats:
                        channel_stats[channel_id] = {
                            'name': channel_title,
                            'id': channel_id,
                            'subscribers': 0,  # Will be filled later if possible
                            'total_views': 0,
                            'video_count': 0,
                            'videos': []
                        }
                    
                    channel_stats[channel_id]['video_count'] += 1
                    channel_stats[channel_id]['videos'].append(item)
            
            # Get detailed channel info for top channels
            channels = list(channel_stats.values())
            
            # Sort by video count first, then get detailed info for top channels
            channels.sort(key=lambda x: x['video_count'], reverse=True)
            
            # Get detailed info for top 10 channels
            for i, channel in enumerate(channels[:10]):
                detailed_info = self.get_channel(channel['id'], use_cache=True)
                if detailed_info:
                    stats = detailed_info.get('statistics', {})
                    channel['subscribers'] = int(stats.get('subscriberCount', 0))
                    channel['total_views'] = int(stats.get('viewCount', 0))
                
                # Small delay between requests
                if i < 9:  # Don't delay after the last one
                    time.sleep(0.5)
            
            return {
                'channels': channels,
                'total': len(channels),
                'data_source': 'yt-dlp'
            }
            
        except Exception as e:
            logger.error(f"Rising stars error for {niche}: {e}")
            return {'channels': [], 'total': 0, 'error': str(e)}
    
    def _convert_search_response(self, ytdlp_results: list, max_results: int, search_type: str) -> dict:
        """Convert yt-dlp search results to YouTube API format"""
        items = []
        
        for item in ytdlp_results[:max_results]:
            try:
                # Skip if item is None or invalid
                if not item or not isinstance(item, dict):
                    continue
                
                # Extract common fields
                video_id = item.get('id', '')
                title = item.get('title', '')
                channel = item.get('uploader', item.get('channel', 'Unknown'))
                channel_id = item.get('uploader_id', item.get('channel_id', ''))
                description = item.get('description', '')
                if description:
                    description = description[:200]  # Truncate
                
                # Convert upload date
                upload_date = item.get('upload_date')
                published_at = self._convert_upload_date(upload_date)
                
                if search_type == 'channel':
                    # Format as channel result
                    youtube_item = {
                        'kind': 'youtube#searchResult',
                        'id': {
                            'kind': 'youtube#channel',
                            'channelId': channel_id or video_id  # Fallback to video_id if no channel_id
                        },
                        'snippet': {
                            'title': channel,
                            'description': description,
                            'channelId': channel_id or video_id,
                            'channelTitle': channel,
                            'thumbnails': {
                                'default': {'url': item.get('thumbnail', '')}
                            }
                        }
                    }
                else:
                    # Format as video result
                    # Get channel handle for proper @ URL (uploader_id already includes @ prefix)
                    uploader_id = item.get('uploader_id', '')
                    channel_url = f"https://www.youtube.com/{uploader_id}" if uploader_id else f"https://www.youtube.com/channel/{channel_id}"
                    
                    youtube_item = {
                        'kind': 'youtube#searchResult',
                        'id': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        },
                        'snippet': {
                            'title': title,
                            'description': description,
                            'channelId': channel_id,
                            'channelTitle': channel,
                            'channelHandle': uploader_id,
                            'channelUrl': channel_url,
                            'publishedAt': published_at,
                            'thumbnails': {
                                'default': {'url': item.get('thumbnail', '')}
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
                'totalResults': len(items) * 100,  # Estimate
                'resultsPerPage': len(items)
            },
            'data_source': 'yt-dlp'
        }
    
    def _extract_channel_from_video(self, video_data: dict, channel_id: str) -> dict:
        """Extract channel information from video metadata"""
        try:
            return {
                'authorId': channel_id,
                'author': video_data.get('uploader', video_data.get('channel', 'Unknown Channel')),
                'subCount': video_data.get('channel_follower_count', 0),
                'totalViews': video_data.get('channel_view_count', 0),  # Not always available
                'videoCount': 1,  # We can't get total video count from single video
                'description': f"Channel data from yt-dlp video metadata",
                'authorUrl': video_data.get('uploader_url', f'https://youtube.com/channel/{channel_id}'),
                'data_source': 'yt-dlp',
                'statistics': {
                    'subscriberCount': str(video_data.get('channel_follower_count', 0)),
                    'viewCount': str(video_data.get('channel_view_count', 0)),
                    'videoCount': str(1)  # Minimum 1 since we found a video
                },
                'snippet': {
                    'title': video_data.get('uploader', video_data.get('channel', 'Unknown Channel')),
                    'description': f"Channel data extracted from yt-dlp",
                    'publishedAt': self._convert_upload_date(video_data.get('upload_date'))
                }
            }
        except Exception as e:
            logger.error(f"Error extracting channel from video: {e}")
            return None
    
    def _convert_upload_date(self, upload_date: str) -> str:
        """Convert yt-dlp upload date (YYYYMMDD) to ISO format"""
        if not upload_date:
            return datetime.now().isoformat() + 'Z'
        
        try:
            # yt-dlp uses YYYYMMDD format
            dt = datetime.strptime(upload_date, '%Y%m%d')
            return dt.isoformat() + 'Z'
        except:
            return datetime.now().isoformat() + 'Z'
    
    def get_call_count(self) -> int:
        """Get number of yt-dlp calls made"""
        return self.call_count


class ContentTypeAnalyzer:
    """
    Analyzes YouTube channel content to detect faceless/safe-to-copy content types
    using metadata-based keyword and pattern analysis (NO AI/vision required)
    """
    
    # Keywords indicating faceless/voice-over content
    FACELESS_KEYWORDS = [
        'faceless', 'no commentary', 'voice over', 'voiceover', 'tts', 'text to speech',
        'ai voice', 'compilation', 'top 10', 'top 5', 'screen recording', 'tutorial',
        'gameplay', 'asmr', 'music mix', 'relaxing', 'meditation', 'stock footage',
        'ambient', 'background music', 'study music', 'sleep music', 'beats',
        'instrumental', 'countdown', 'timer', 'automation', 'auto generated'
    ]
    
    # Keywords for specific content types  
    COMPILATION_KEYWORDS = ['compilation', 'top 10', 'top 5', 'best of', 'countdown', 'list']
    SCREEN_RECORDING_KEYWORDS = ['screen recording', 'tutorial', 'walkthrough', 'how to', 'guide']
    TUTORIAL_KEYWORDS = ['tutorial', 'how to', 'guide', 'learn', 'course', 'lesson']
    VOICEOVER_KEYWORDS = ['voice over', 'voiceover', 'narration', 'tts', 'text to speech', 'ai voice']
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_channel(self, channel_data: dict) -> dict:
        """
        Analyze channel data to detect content type and faceless indicators
        
        Args:
            channel_data: Channel data from yt-dlp/API containing channel info and videos
            
        Returns:
            dict: {
                'faceless_score': int,  # 0-100 likelihood of faceless content
                'content_type': str,    # "faceless_voiceover" | "compilation" | etc
                'copy_indicators': list,  # detected keywords/patterns
                'analysis_details': dict  # breakdown of scoring
            }
        """
        try:
            # Extract analysis text from channel data
            channel_title = channel_data.get('snippet', {}).get('title', '')
            channel_desc = channel_data.get('snippet', {}).get('description', '')
            
            # Get video data for pattern analysis
            videos = channel_data.get('videos', [])
            if not videos and 'items' in channel_data:
                videos = channel_data['items']
            
            # Analyze different aspects
            title_analysis = self._analyze_text(channel_title, "channel_title")
            desc_analysis = self._analyze_text(channel_desc, "channel_description")
            video_analysis = self._analyze_videos(videos)
            upload_pattern = self._analyze_upload_frequency(videos)
            duration_pattern = self._analyze_video_durations(videos)
            
            # Combine analyses
            total_score = 0
            copy_indicators = []
            details = {}
            
            # Title analysis (weight: 20%)
            title_score = title_analysis['score']
            total_score += title_score * 0.2
            copy_indicators.extend(title_analysis['indicators'])
            details['title_analysis'] = title_analysis
            
            # Description analysis (weight: 25%)
            desc_score = desc_analysis['score']
            total_score += desc_score * 0.25
            copy_indicators.extend(desc_analysis['indicators'])
            details['description_analysis'] = desc_analysis
            
            # Video content analysis (weight: 35%)
            video_score = video_analysis['score']
            total_score += video_score * 0.35
            copy_indicators.extend(video_analysis['indicators'])
            details['video_analysis'] = video_analysis
            
            # Upload frequency analysis (weight: 10%)
            upload_score = upload_pattern['score']
            total_score += upload_score * 0.1
            details['upload_pattern'] = upload_pattern
            
            # Duration pattern analysis (weight: 10%)
            duration_score = duration_pattern['score']
            total_score += duration_score * 0.1
            details['duration_pattern'] = duration_pattern
            
            # Determine content type based on indicators
            content_type = self._determine_content_type(copy_indicators, total_score)
            
            return {
                'faceless_score': min(100, max(0, int(total_score))),
                'content_type': content_type,
                'copy_indicators': list(set(copy_indicators)),  # Remove duplicates
                'analysis_details': details
            }
            
        except Exception as e:
            self.logger.error(f"Content type analysis failed: {e}")
            return {
                'faceless_score': 0,
                'content_type': 'unknown',
                'copy_indicators': [],
                'analysis_details': {'error': str(e)}
            }
    
    def _analyze_text(self, text: str, source: str) -> dict:
        """Analyze text for faceless content keywords"""
        if not text:
            return {'score': 0, 'indicators': [], 'matches': []}
            
        text_lower = text.lower()
        matches = []
        indicators = []
        
        for keyword in self.FACELESS_KEYWORDS:
            if keyword in text_lower:
                matches.append(f"{keyword} (in {source})")
                indicators.append(keyword)
        
        # Score based on keyword density
        score = min(100, len(matches) * 15)
        
        return {
            'score': score,
            'indicators': indicators,
            'matches': matches
        }
    
    def _analyze_videos(self, videos: list) -> dict:
        """Analyze video titles and descriptions for patterns"""
        if not videos:
            return {'score': 0, 'indicators': [], 'pattern_count': 0}
            
        total_videos = len(videos)
        faceless_video_count = 0
        indicators = []
        
        for video in videos[:10]:  # Analyze first 10 videos
            video_title = ''
            video_desc = ''
            
            # Extract video info from different data structures
            if isinstance(video, dict):
                if 'snippet' in video:
                    video_title = video['snippet'].get('title', '')
                    video_desc = video['snippet'].get('description', '')
                else:
                    video_title = video.get('title', '')
                    video_desc = video.get('description', '')
            
            # Check for faceless indicators
            combined_text = f"{video_title} {video_desc}".lower()
            
            video_indicators = []
            for keyword in self.FACELESS_KEYWORDS:
                if keyword in combined_text:
                    video_indicators.append(keyword)
            
            if video_indicators:
                faceless_video_count += 1
                indicators.extend(video_indicators)
        
        # Calculate score based on percentage of faceless videos
        faceless_ratio = faceless_video_count / min(total_videos, 10)
        score = faceless_ratio * 100
        
        return {
            'score': score,
            'indicators': list(set(indicators)),
            'pattern_count': faceless_video_count,
            'analyzed_videos': min(total_videos, 10)
        }
    
    def _analyze_upload_frequency(self, videos: list) -> dict:
        """Analyze upload frequency patterns (faceless channels often upload more)"""
        if len(videos) < 3:
            return {'score': 0, 'frequency': 'insufficient_data'}
        
        # Count uploads per week (simplified analysis)
        uploads_per_week = len(videos) / 4  # Assume videos are from last month
        
        # Faceless channels typically upload 3-7x per week
        if 3 <= uploads_per_week <= 7:
            score = 60
            frequency = 'high_faceless_pattern'
        elif uploads_per_week > 7:
            score = 80  # Very high frequency suggests automated/faceless content
            frequency = 'very_high'
        elif uploads_per_week >= 1:
            score = 30
            frequency = 'moderate'
        else:
            score = 10
            frequency = 'low'
        
        return {
            'score': score,
            'frequency': frequency,
            'uploads_per_week': round(uploads_per_week, 1)
        }
    
    def _analyze_video_durations(self, videos: list) -> dict:
        """Analyze video duration patterns"""
        if not videos:
            return {'score': 0, 'pattern': 'no_data'}
        
        durations = []
        for video in videos[:10]:
            duration = 0
            if isinstance(video, dict):
                # Try to extract duration from various formats
                if 'contentDetails' in video:
                    duration_str = video['contentDetails'].get('duration', '')
                    duration = self._parse_duration(duration_str)
                elif 'duration' in video:
                    duration = video.get('duration', 0)
            
            if duration > 0:
                durations.append(duration)
        
        if not durations:
            return {'score': 0, 'pattern': 'no_duration_data'}
        
        avg_duration = sum(durations) / len(durations)
        avg_duration_minutes = avg_duration / 60
        
        # Faceless content patterns:
        # Compilations: 8-20 minutes
        # Screen recordings: 5-15 minutes  
        # ASMR/ambient: 10-60+ minutes
        if 5 <= avg_duration_minutes <= 20:
            score = 70
            pattern = 'faceless_optimal_range'
        elif 3 <= avg_duration_minutes <= 25:
            score = 50
            pattern = 'possible_faceless_range'
        else:
            score = 20
            pattern = 'outside_typical_range'
        
        return {
            'score': score,
            'pattern': pattern,
            'avg_duration_minutes': round(avg_duration_minutes, 1)
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube duration string (PT1H2M3S) to seconds"""
        if not duration_str or not duration_str.startswith('PT'):
            return 0
            
        # Simple regex-free parsing
        duration_str = duration_str[2:]  # Remove PT
        seconds = 0
        
        if 'H' in duration_str:
            hours_part = duration_str.split('H')[0]
            if hours_part.isdigit():
                seconds += int(hours_part) * 3600
            duration_str = duration_str.split('H')[1]
        
        if 'M' in duration_str:
            minutes_part = duration_str.split('M')[0]
            if minutes_part.isdigit():
                seconds += int(minutes_part) * 60
            duration_str = duration_str.split('M')[1]
        
        if 'S' in duration_str:
            seconds_part = duration_str.replace('S', '')
            if seconds_part.isdigit():
                seconds += int(seconds_part)
        
        return seconds
    
    def _determine_content_type(self, indicators: list, total_score: int) -> str:
        """Determine the most likely content type based on indicators"""        
        indicator_text = ' '.join(indicators).lower()
        
        # Check for specific content types
        compilation_matches = sum(1 for kw in self.COMPILATION_KEYWORDS if kw in indicator_text)
        screen_recording_matches = sum(1 for kw in self.SCREEN_RECORDING_KEYWORDS if kw in indicator_text)
        tutorial_matches = sum(1 for kw in self.TUTORIAL_KEYWORDS if kw in indicator_text)
        voiceover_matches = sum(1 for kw in self.VOICEOVER_KEYWORDS if kw in indicator_text)
        
        # Determine primary type - keyword matches override low scores
        if compilation_matches >= 2:
            return 'compilation'
        elif tutorial_matches >= 1 and screen_recording_matches >= 1:
            return 'tutorial'  # Tutorial + screen recording = educational content
        elif tutorial_matches >= 1:  # Single tutorial match is enough
            return 'tutorial'
        elif screen_recording_matches >= 1:  # Single screen recording match
            return 'screen_recording'
        elif voiceover_matches >= 1:
            return 'faceless_voiceover'
        elif total_score >= 60:
            return 'faceless_voiceover'  # Default high-score type
        elif total_score >= 30:
            return 'possibly_faceless'
        elif total_score > 0:  # Any indicators found
            return 'possibly_faceless'
        else:
            return 'unknown'