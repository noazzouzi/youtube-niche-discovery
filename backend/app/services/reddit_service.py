"""
Reddit Service - Community analysis for niche discovery
Implements Reddit API integration for PM Agent's 100-point scoring algorithm
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime, timedelta
import json
import re

import praw
import prawcore
from app.models.metric import Metric
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedditService:
    """
    Reddit service for niche discovery and content source analysis
    
    Provides data for:
    - Content Availability Score (5 points of 15 total) 
    - Community engagement metrics
    - Content source validation
    - Subreddit discovery for new niches
    """
    
    def __init__(self):
        # Initialize Reddit API client
        self.reddit = None
        try:
            if hasattr(settings, 'REDDIT_CLIENT_ID') and settings.REDDIT_CLIENT_ID:
                self.reddit = praw.Reddit(
                    client_id=settings.REDDIT_CLIENT_ID,
                    client_secret=settings.REDDIT_CLIENT_SECRET,
                    user_agent=settings.REDDIT_USER_AGENT or "NicheDiscovery/1.0"
                )
            else:
                logger.warning("Reddit API credentials not configured")
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
        
        self.rate_limit_delay = 1.0  # Seconds between requests
    
    async def collect_reddit_metrics(self, niche_id: int, niche_name: str, keywords: List[str]) -> List[Metric]:
        """
        Collect Reddit metrics for niche scoring
        
        Returns metrics for:
        - reddit_total_members (community size)
        - reddit_activity_score (post frequency and engagement)
        - reddit_content_score (content quality and relevance)
        """
        metrics = []
        
        if not self.reddit:
            logger.warning("Reddit client not available, skipping Reddit metrics")
            return metrics
        
        try:
            # Find relevant subreddits for this niche
            relevant_subreddits = await self._find_relevant_subreddits(niche_name, keywords)
            
            if relevant_subreddits:
                # Analyze top subreddits
                subreddit_data = await self._analyze_subreddits(relevant_subreddits[:10])
                
                # Create metrics from analysis
                total_members = sum(sub.get('members', 0) for sub in subreddit_data)
                avg_activity = sum(sub.get('activity_score', 0) for sub in subreddit_data) / max(len(subreddit_data), 1)
                content_quality = sum(sub.get('content_score', 0) for sub in subreddit_data) / max(len(subreddit_data), 1)
                
                # Total members metric (used in PM scoring)
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=3,  # Reddit source
                    metric_type="content_availability",
                    metric_name="reddit_total_members",
                    value=float(total_members),
                    period="current",
                    confidence_score=90.0,
                    collected_at=datetime.utcnow(),
                    raw_data=json.dumps(subreddit_data)
                ))
                
                # Activity score
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=3,
                    metric_type="content_availability",
                    metric_name="reddit_activity_score",
                    value=avg_activity,
                    period="current",
                    confidence_score=85.0,
                    collected_at=datetime.utcnow()
                ))
                
                # Content quality score
                metrics.append(Metric(
                    niche_id=niche_id,
                    source_id=3,
                    metric_type="content_availability", 
                    metric_name="reddit_content_quality",
                    value=content_quality,
                    period="current",
                    confidence_score=80.0,
                    collected_at=datetime.utcnow()
                ))
                
                logger.info(f"Collected Reddit metrics for niche '{niche_name}': {total_members} total members across {len(subreddit_data)} subreddits")
            
            else:
                logger.warning(f"No relevant subreddits found for niche '{niche_name}'")
        
        except Exception as e:
            logger.error(f"Error collecting Reddit metrics for '{niche_name}': {e}")
        
        return metrics
    
    async def _find_relevant_subreddits(self, niche_name: str, keywords: List[str]) -> List[str]:
        """Find subreddits relevant to the niche"""
        relevant_subs = []
        
        try:
            search_terms = [niche_name] + keywords[:5]  # Limit search terms
            
            for term in search_terms:
                # Clean the search term
                clean_term = re.sub(r'[^\w\s]', '', term).strip()
                if len(clean_term) < 3:
                    continue
                
                # Search for subreddits
                found_subs = await self._search_subreddits(clean_term)
                relevant_subs.extend(found_subs)
                
                await asyncio.sleep(self.rate_limit_delay)
            
            # Remove duplicates and return unique subreddits
            return list(set(relevant_subs))
        
        except Exception as e:
            logger.error(f"Error finding relevant subreddits: {e}")
            return []
    
    async def _search_subreddits(self, query: str) -> List[str]:
        """Search for subreddits by query"""
        subreddits = []
        
        try:
            loop = asyncio.get_event_loop()
            
            def _search():
                try:
                    # Search subreddits using Reddit API
                    search_results = self.reddit.subreddits.search(query, limit=10)
                    return [sub.display_name for sub in search_results]
                except prawcore.exceptions.NotFound:
                    return []
                except Exception as e:
                    logger.error(f"Error searching subreddits for '{query}': {e}")
                    return []
            
            subreddits = await loop.run_in_executor(None, _search)
            
            # Also try exact match and variations
            exact_variations = [
                query.lower(),
                query.replace(' ', ''),
                query.replace(' ', '_'),
                f"{query}s",
                f"r{query}"
            ]
            
            for variation in exact_variations:
                try:
                    def _check_sub():
                        try:
                            sub = self.reddit.subreddit(variation)
                            # Try to access the subreddit to verify it exists
                            _ = sub.subscribers
                            return variation
                        except:
                            return None
                    
                    result = await loop.run_in_executor(None, _check_sub)
                    if result:
                        subreddits.append(result)
                    
                    await asyncio.sleep(0.1)  # Small delay
                    
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Error in subreddit search: {e}")
        
        return list(set(subreddits))  # Remove duplicates
    
    async def _analyze_subreddits(self, subreddit_names: List[str]) -> List[Dict[str, Any]]:
        """Analyze subreddits for metrics"""
        subreddit_data = []
        
        for sub_name in subreddit_names:
            try:
                sub_analysis = await self._analyze_single_subreddit(sub_name)
                if sub_analysis:
                    subreddit_data.append(sub_analysis)
                
                await asyncio.sleep(self.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error analyzing subreddit r/{sub_name}: {e}")
                continue
        
        return subreddit_data
    
    async def _analyze_single_subreddit(self, subreddit_name: str) -> Optional[Dict[str, Any]]:
        """Analyze a single subreddit for metrics"""
        try:
            loop = asyncio.get_event_loop()
            
            def _analyze():
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get basic info
                    members = subreddit.subscribers
                    description = subreddit.description[:500] if subreddit.description else ""
                    created = datetime.fromtimestamp(subreddit.created_utc) if subreddit.created_utc else None
                    
                    # Get recent posts for activity analysis
                    recent_posts = []
                    try:
                        for post in subreddit.hot(limit=25):
                            recent_posts.append({
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'created': datetime.fromtimestamp(post.created_utc),
                                'title': post.title[:100]
                            })
                    except:
                        pass  # Some subreddits might be private or have restrictions
                    
                    return {
                        'name': subreddit_name,
                        'members': members,
                        'description': description,
                        'created': created.isoformat() if created else None,
                        'posts_analyzed': len(recent_posts),
                        'recent_posts': recent_posts
                    }
                
                except prawcore.exceptions.Forbidden:
                    logger.warning(f"Access forbidden to r/{subreddit_name}")
                    return None
                except prawcore.exceptions.NotFound:
                    logger.warning(f"Subreddit r/{subreddit_name} not found")
                    return None
                except Exception as e:
                    logger.error(f"Error analyzing r/{subreddit_name}: {e}")
                    return None
            
            subreddit_info = await loop.run_in_executor(None, _analyze)
            
            if subreddit_info and subreddit_info['members'] > 0:
                # Calculate activity and content scores
                activity_score = self._calculate_activity_score(subreddit_info)
                content_score = self._calculate_content_score(subreddit_info)
                
                return {
                    'subreddit': subreddit_name,
                    'members': subreddit_info['members'],
                    'activity_score': activity_score,
                    'content_score': content_score,
                    'posts_analyzed': subreddit_info['posts_analyzed'],
                    'created': subreddit_info['created']
                }
        
        except Exception as e:
            logger.error(f"Error in subreddit analysis: {e}")
        
        return None
    
    def _calculate_activity_score(self, subreddit_info: Dict[str, Any]) -> float:
        """Calculate activity score based on post frequency and engagement"""
        try:
            recent_posts = subreddit_info.get('recent_posts', [])
            members = subreddit_info.get('members', 1)
            
            if not recent_posts:
                return 0.0
            
            # Calculate average engagement
            total_score = sum(post.get('score', 0) for post in recent_posts)
            total_comments = sum(post.get('num_comments', 0) for post in recent_posts)
            
            avg_score = total_score / len(recent_posts)
            avg_comments = total_comments / len(recent_posts)
            
            # Normalize by member count (engagement rate)
            engagement_rate = (avg_score + avg_comments) / max(members / 1000, 1)  # Per 1000 members
            
            # Scale to 0-100
            activity_score = min(engagement_rate * 10, 100)
            
            return activity_score
        
        except Exception as e:
            logger.error(f"Error calculating activity score: {e}")
            return 0.0
    
    def _calculate_content_score(self, subreddit_info: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        try:
            members = subreddit_info.get('members', 0)
            posts_analyzed = subreddit_info.get('posts_analyzed', 0)
            description = subreddit_info.get('description', '')
            
            # Base score from member count (more members = more content potential)
            if members >= 1000000:
                member_score = 40
            elif members >= 100000:
                member_score = 30
            elif members >= 10000:
                member_score = 20
            elif members >= 1000:
                member_score = 15
            else:
                member_score = 10
            
            # Content variety score (based on post count)
            variety_score = min(posts_analyzed * 2, 30)  # Max 30 points
            
            # Description quality score
            desc_score = min(len(description) / 10, 30)  # Max 30 points
            
            total_score = member_score + variety_score + desc_score
            return min(total_score, 100)
        
        except Exception as e:
            logger.error(f"Error calculating content score: {e}")
            return 0.0
    
    async def discover_trending_communities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Discover trending communities that could indicate new niches
        """
        trending_communities = []
        
        if not self.reddit:
            return trending_communities
        
        try:
            loop = asyncio.get_event_loop()
            
            def _get_trending():
                try:
                    # Get popular/trending subreddits
                    popular_subs = []
                    
                    # Get subreddits from popular posts
                    for post in self.reddit.subreddit('popular').hot(limit=100):
                        sub_name = post.subreddit.display_name
                        if sub_name not in popular_subs and len(popular_subs) < limit:
                            popular_subs.append(sub_name)
                    
                    return popular_subs
                
                except Exception as e:
                    logger.error(f"Error getting trending communities: {e}")
                    return []
            
            popular_sub_names = await loop.run_in_executor(None, _get_trending)
            
            # Analyze trending communities for niche potential
            for sub_name in popular_sub_names[:20]:  # Limit analysis
                try:
                    sub_analysis = await self._analyze_single_subreddit(sub_name)
                    
                    if sub_analysis and sub_analysis['members'] >= 10000:  # Minimum threshold
                        # Calculate trend potential
                        trend_score = self._calculate_trend_potential(sub_analysis)
                        
                        trending_communities.append({
                            "name": sub_name,
                            "description": f"Community with {sub_analysis['members']:,} members",
                            "category": "reddit_community",
                            "keywords": [sub_name],
                            "discovery_source": "reddit_trending",
                            "trend_score": trend_score,
                            "member_count": sub_analysis['members'],
                            "activity_score": sub_analysis['activity_score']
                        })
                    
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.error(f"Error analyzing trending community r/{sub_name}: {e}")
                    continue
            
            # Sort by trend score
            trending_communities.sort(key=lambda x: x["trend_score"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error discovering trending communities: {e}")
        
        return trending_communities[:limit]
    
    def _calculate_trend_potential(self, subreddit_analysis: Dict[str, Any]) -> float:
        """Calculate trend potential score for a subreddit"""
        try:
            members = subreddit_analysis.get('members', 0)
            activity_score = subreddit_analysis.get('activity_score', 0)
            content_score = subreddit_analysis.get('content_score', 0)
            
            # Weight factors
            member_weight = 0.4
            activity_weight = 0.3
            content_weight = 0.3
            
            # Normalize member count (log scale)
            import math
            member_score = min(math.log10(max(members, 1)) * 10, 100)
            
            # Calculate weighted score
            trend_score = (
                member_score * member_weight +
                activity_score * activity_weight +
                content_score * content_weight
            )
            
            return min(trend_score, 100)
        
        except Exception as e:
            logger.error(f"Error calculating trend potential: {e}")
            return 0.0