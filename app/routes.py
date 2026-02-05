"""
Request Handler Module for YouTube Niche Discovery Engine

This module handles HTTP API routes for niche analysis, channel discovery,
competitor analysis, and system status endpoints.
"""

import json
import time
import random
import logging
from urllib.parse import urlparse, parse_qs
from typing import Dict

from .suggestions import NICHE_SUGGESTIONS

logger = logging.getLogger(__name__)

# Global state - will be set by server.py
_shared_components = None

def set_shared_components(components):
    """Set shared components from server.py"""
    global _shared_components
    _shared_components = components

def get_shared_components():
    """Get shared components"""
    if _shared_components is None:
        raise RuntimeError("Shared components not initialized")
    return _shared_components


class RequestHandler:
    """HTTP request handler with shared components"""
    
    def __init__(self):
        pass
    
    async def handle_analyze(self, query_params: dict) -> dict:
        """Handle /api/analyze route"""
        niche = query_params.get('niche', [''])[0]
        if not niche:
            return {'error': 'Please provide a niche'}
        
        result = await self.analyze_niche(niche)
        return result
    
    async def handle_channels(self, query_params: dict) -> dict:
        """Handle /api/channels route"""
        niche = query_params.get('niche', [''])[0]
        if not niche:
            return {'error': 'Please provide a niche parameter'}
        
        result = await self.discover_channels(niche)
        return result
    
    async def handle_competitors(self, query_params: dict) -> dict:
        """Handle /api/competitors route"""
        niche = query_params.get('niche', [''])[0]
        if not niche:
            return {'error': 'Please provide a niche parameter'}
        
        result = await self.analyze_competitors(niche)
        return result
    
    async def handle_suggestions(self, query_params: dict) -> dict:
        """Handle /api/suggestions route"""
        return self.get_suggestions()
    
    async def handle_stats(self, query_params: dict) -> dict:
        """Handle /api/stats route"""
        return self.get_stats()
    
    async def handle_status(self, query_params: dict) -> dict:
        """Handle /api/status route"""
        return self.get_status()
    
    async def analyze_niche(self, niche_name: str) -> dict:
        """Analyze niche with two-phase scoring approach"""
        start_time = time.time()
        logger.info(f"Analyzing niche: {niche_name}")
        
        try:
            cache, ytdlp_data_source, trends_api, niche_scorer, recommendation_engine, channel_discovery, competitor_analyzer, content_type_analyzer = get_shared_components()
            
            # Get full score for the main niche
            result = niche_scorer.full_score(niche_name)
            
            # Get recommendations using two-phase approach
            recommendations = recommendation_engine.get_recommendations(
                niche_name, result['total_score']
            )
            
            # Get rising star channels
            rising_star_channels = channel_discovery.find_rising_star_channels(niche_name)
            
            result['recommendations'] = recommendations
            result['rising_star_channels'] = rising_star_channels
            result['recommendation'] = self._get_recommendation_text(result['total_score'])
            
            # Add performance stats
            analysis_time = time.time() - start_time
            result['performance'] = {
                'analysis_time_seconds': round(analysis_time, 2),
                'ytdlp_api_calls': ytdlp_data_source.call_count,
                'trends_api_calls': trends_api.call_count,
                'cache_stats': cache.get_stats()
            }
            
            logger.info(f"Analysis completed in {analysis_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Analysis error for {niche_name}: {e}")
            raise
    
    async def discover_channels(self, niche: str) -> dict:
        """Discover rising star channels for a niche"""
        start_time = time.time()
        logger.info(f"Discovering channels for: {niche}")
        
        try:
            cache, ytdlp_data_source, trends_api, niche_scorer, recommendation_engine, channel_discovery, competitor_analyzer, content_type_analyzer = get_shared_components()
            
            # Get channel discovery results
            result = channel_discovery.find_rising_star_channels(niche)
            
            # Add API stats
            discovery_time = time.time() - start_time
            result['performance'] = {
                'discovery_time_seconds': round(discovery_time, 2),
                'ytdlp_api_calls': ytdlp_data_source.call_count,
                'cache_stats': cache.get_stats()
            }
            
            logger.info(f"Channel discovery completed in {discovery_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Channel discovery error for {niche}: {e}")
            return {
                'niche': niche,
                'channels': [],
                'analysis': {
                    'total_channels_found': 0,
                    'rising_stars_identified': 0,
                    'best_opportunity': None,
                    'error_reason': f'Error: {str(e)}'
                },
                'success': False
            }
    
    async def analyze_competitors(self, niche: str) -> dict:
        """Analyze competitor landscape for a niche"""
        start_time = time.time()
        logger.info(f"Analyzing competitors for: {niche}")
        
        try:
            cache, ytdlp_data_source, trends_api, niche_scorer, recommendation_engine, channel_discovery, competitor_analyzer, content_type_analyzer = get_shared_components()
            
            # Get competitor analysis results
            result = competitor_analyzer.analyze_competitors(niche)
            
            # Add API performance stats
            analysis_time = time.time() - start_time
            if result.get('performance'):
                result['performance'].update({
                    'api_analysis_time_seconds': round(analysis_time, 2),
                    'cache_stats': cache.get_stats()
                })
            
            logger.info(f"Competitor analysis completed in {analysis_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Competitor analysis error for {niche}: {e}")
            return {
                'niche': niche,
                'saturation_level': 'unknown',
                'saturation_score': 0,
                'channel_count': 0,
                'tier_breakdown': {'micro': 0, 'small': 0, 'medium': 0, 'large': 0},
                'top_competitors': [],
                'error_reason': f'Error: {str(e)}',
                'success': False
            }
    
    def get_suggestions(self) -> dict:
        """Get random niche suggestions"""
        suggestions = []
        categories = list(NICHE_SUGGESTIONS.keys())
        random.shuffle(categories)
        
        for cat in categories[:4]:
            niches = NICHE_SUGGESTIONS[cat]
            suggestions.append({
                'category': cat,
                'niches': random.sample(niches, min(3, len(niches)))
            })
        
        return {'suggestions': suggestions}
    
    def get_stats(self) -> dict:
        """Get comprehensive API statistics"""
        cache, ytdlp_data_source, trends_api, _, _, _, _, _ = get_shared_components()
        # Note: Need to get uptime and request count from server.py
        return {
            'uptime_seconds': 0,  # Will be set by server
            'total_requests': 0,  # Will be set by server
            'requests_per_minute': 0,  # Will be set by server
            'api_calls': {
                'yt_dlp': ytdlp_data_source.call_count,
                'trends': trends_api.call_count,
                'total': ytdlp_data_source.call_count + trends_api.call_count
            },
            'cache': cache.get_stats(),
            'memory': {
                'cached_entries': len(cache.cache),
                'expired_cleaned': cache.clear_expired()
            }
        }
    
    def get_status(self) -> dict:
        """Get system status"""
        return {
            'status': 'live',
            'version': 'ytdlp_v3.0_refactored',
            'api': 'YT-DLP ✅ (No API keys required)',
            'data_source': 'yt-dlp direct scraping',
            'caching': 'ENABLED ✅',
            'two_phase_scoring': 'ENABLED ✅',
            'uptime': 0  # Will be set by server
        }
    
    def _get_recommendation_text(self, score: float) -> str:
        """Get recommendation text based on score"""
        if score >= 85: return "🔥 Excellent niche—high potential for growth!"
        elif score >= 75: return "✅ Great niche with strong opportunities"
        elif score >= 65: return "👍 Good niche worth exploring"
        elif score >= 55: return "⚠️ Moderate potential—research further"
        return "❌ Challenging niche—consider alternatives"