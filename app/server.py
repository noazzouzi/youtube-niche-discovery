"""
Main Server Module for YouTube Niche Discovery Engine

This is the entry point for the refactored application. It uses aiohttp
for async HTTP serving, initializes all shared components, serves static
files and templates, and routes API requests to the RequestHandler.
"""

import os
import sys
import time
import json
import asyncio
import logging
from pathlib import Path

from aiohttp import web

# Ensure parent directory is on path for ytdlp_data_source import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .cache import APICache
from .ytdlp_client import YtDlpClient
from .youtube_api import YouTubeAPI
from .trends import TrendsAPI
from .scorer import NicheScorer
from .recommendations import RecommendationEngine
from .discovery import ChannelDiscovery
from .competitors import CompetitorAnalyzer
from .routes import RequestHandler, set_shared_components

from ytdlp_data_source import YtDlpDataSource, ContentTypeAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

# Global state
_start_time = time.time()
_request_count = 0


def init_shared_components():
    """Initialize all shared component instances"""
    logger.info("Initializing shared components...")
    
    cache = APICache(ttl_seconds=3600)
    ytdlp_data_source = YtDlpDataSource(cache)
    trends_api = TrendsAPI(cache)
    niche_scorer = NicheScorer(ytdlp_data_source, trends_api)
    recommendation_engine = RecommendationEngine(niche_scorer)
    channel_discovery = ChannelDiscovery(ytdlp_data_source, cache)
    competitor_analyzer = CompetitorAnalyzer(ytdlp_data_source, cache)
    content_type_analyzer = ContentTypeAnalyzer()
    
    components = (
        cache, ytdlp_data_source, trends_api, niche_scorer,
        recommendation_engine, channel_discovery, competitor_analyzer,
        content_type_analyzer
    )
    set_shared_components(components)
    
    logger.info("Shared components initialized ✅")
    return components


async def handle_index(request):
    """Serve the main HTML page from templates/"""
    index_path = TEMPLATES_DIR / 'index.html'
    if index_path.exists():
        return web.FileResponse(index_path)
    else:
        return web.Response(text="index.html not found", status=404)


async def handle_api(request):
    """Route API requests to the RequestHandler"""
    global _request_count
    _request_count += 1
    
    path = request.path
    query_params = {}
    for key, value in request.query.items():
        if key in query_params:
            query_params[key].append(value)
        else:
            query_params[key] = [value]
    
    handler = RequestHandler()
    
    route_map = {
        '/api/analyze': handler.handle_analyze,
        '/api/channels': handler.handle_channels,
        '/api/competitors': handler.handle_competitors,
        '/api/suggestions': handler.handle_suggestions,
        '/api/stats': handler.handle_stats,
        '/api/status': handler.handle_status,
    }
    
    route_fn = route_map.get(path)
    if not route_fn:
        return web.json_response({'error': 'Not found'}, status=404)
    
    try:
        # Run blocking operations in a thread pool to avoid blocking the event loop
        result = await route_fn(query_params)
        
        # Inject server-level stats for stats/status endpoints
        if path == '/api/stats':
            uptime = time.time() - _start_time
            result['uptime_seconds'] = round(uptime, 1)
            result['total_requests'] = _request_count
            result['requests_per_minute'] = round(_request_count / (uptime / 60), 2) if uptime > 0 else 0
        elif path == '/api/status':
            result['uptime'] = round(time.time() - _start_time, 1)
        
        return web.json_response(result)
    except Exception as e:
        logger.error(f"API error on {path}: {e}")
        return web.json_response({'error': f'Internal error: {str(e)}'}, status=500)


def create_app():
    """Create and configure the aiohttp application"""
    app = web.Application()
    
    # API routes
    app.router.add_get('/api/analyze', handle_api)
    app.router.add_get('/api/channels', handle_api)
    app.router.add_get('/api/competitors', handle_api)
    app.router.add_get('/api/suggestions', handle_api)
    app.router.add_get('/api/stats', handle_api)
    app.router.add_get('/api/status', handle_api)
    
    # Static files (CSS, JS)
    if STATIC_DIR.exists():
        app.router.add_static('/static', STATIC_DIR)
    
    # Root serves the HTML template
    app.router.add_get('/', handle_index)
    
    # CORS middleware
    @web.middleware
    async def cors_middleware(request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    
    app.middlewares.append(cors_middleware)
    
    return app


def main():
    """Start the server"""
    logger.info("🎯 YouTube Niche Discovery Engine (Refactored)")
    logger.info(f"💻 Local: http://localhost:8080")
    logger.info(f"🌍 External: http://38.143.19.241:8080")
    logger.info(f"📁 Templates: {TEMPLATES_DIR}")
    logger.info(f"📁 Static: {STATIC_DIR}")
    logger.info("🚀 Server starting...")
    
    # Initialize components
    init_shared_components()
    
    # Create and run app
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8080, print=lambda msg: logger.info(msg))


if __name__ == '__main__':
    main()
