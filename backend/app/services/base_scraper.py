"""
Base Scraper Class - Common functionality for all scrapers
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.source import Source
from app.models.niche import Niche
from app.models.metric import Metric

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all data scrapers"""
    
    def __init__(self, source_name: str, session: AsyncSession):
        self.source_name = source_name
        self.session = session
        self.source: Optional[Source] = None
        self.client_session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
    async def initialize(self):
        """Initialize the scraper"""
        # Get source configuration
        from sqlalchemy import select
        query = select(Source).where(Source.name == self.source_name)
        result = await self.session.execute(query)
        self.source = result.scalar_one_or_none()
        
        if not self.source:
            raise ValueError(f"Source '{self.source_name}' not found in database")
        
        if not self.source.is_active:
            raise ValueError(f"Source '{self.source_name}' is not active")
        
        # Initialize HTTP client
        self.client_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT),
            headers={"User-Agent": settings.USER_AGENT}
        )
        
        logger.info(f"Initialized scraper for {self.source_name}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client_session:
            await self.client_session.close()
        logger.info(f"Cleaned up scraper for {self.source_name}")
    
    @abstractmethod
    async def scrape_trending(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape trending content/niches from the source"""
        pass
    
    @abstractmethod
    async def scrape_niche_data(self, niche_name: str) -> Dict[str, Any]:
        """Scrape detailed data for a specific niche"""
        pass
    
    async def rate_limit_check(self) -> bool:
        """Check if we can make a request without hitting rate limits"""
        if not self.source:
            return False
        
        # Simple check - in production, this would be more sophisticated
        return self.source.requests_remaining_today > 0
    
    async def make_request(self, url: str, **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Make a rate-limited HTTP request"""
        if not await self.rate_limit_check():
            logger.warning(f"Rate limit reached for {self.source_name}")
            return None
        
        if not self.client_session:
            raise RuntimeError("Client session not initialized")
        
        try:
            start_time = datetime.now()
            response = await self.client_session.get(url, **kwargs)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds()
            
            # Update source performance metrics
            success = response.status == 200
            self.source.update_performance_metrics(success, response_time)
            
            if success:
                self.source.last_successful_request = datetime.utcnow()
            else:
                self.source.last_error = f"HTTP {response.status}: {response.reason}"
            
            await self.session.commit()
            
            # Add delay to respect rate limits
            await asyncio.sleep(settings.SCRAPING_DELAY)
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed for {self.source_name}: {e}")
            self.source.update_performance_metrics(False, 0)
            self.source.last_error = str(e)
            await self.session.commit()
            return None
    
    async def save_niche(self, niche_data: Dict[str, Any]) -> Niche:
        """Save discovered niche to database"""
        from sqlalchemy import select
        
        # Check if niche already exists
        existing_query = select(Niche).where(Niche.name == niche_data["name"])
        existing_result = await self.session.execute(existing_query)
        existing_niche = existing_result.scalar_one_or_none()
        
        if existing_niche:
            logger.info(f"Niche '{niche_data['name']}' already exists")
            return existing_niche
        
        # Create new niche
        niche = Niche(
            name=niche_data["name"],
            description=niche_data.get("description"),
            keywords=niche_data.get("keywords", []),
            category=niche_data.get("category"),
            discovery_source=self.source_name,
            discovery_method=niche_data.get("discovery_method", "scraping"),
            additional_data=niche_data.get("additional_data", {})
        )
        
        self.session.add(niche)
        await self.session.commit()
        await self.session.refresh(niche)
        
        logger.info(f"Saved new niche: {niche.name}")
        return niche
    
    async def save_metrics(self, niche: Niche, metrics_data: List[Dict[str, Any]]) -> List[Metric]:
        """Save metrics for a niche"""
        metrics = []
        
        for metric_data in metrics_data:
            metric = Metric(
                niche_id=niche.id,
                source_id=self.source.id,
                metric_type=metric_data["metric_type"],
                metric_name=metric_data["metric_name"],
                value=metric_data["value"],
                normalized_value=metric_data.get("normalized_value"),
                period=metric_data.get("period"),
                collection_method="scraping",
                confidence_score=metric_data.get("confidence_score", 100.0),
                raw_data=metric_data.get("raw_data", {}),
                additional_metrics=metric_data.get("additional_metrics", {})
            )
            
            metrics.append(metric)
            self.session.add(metric)
        
        await self.session.commit()
        
        for metric in metrics:
            await self.session.refresh(metric)
        
        logger.info(f"Saved {len(metrics)} metrics for niche: {niche.name}")
        return metrics
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (basic implementation)"""
        if not text:
            return []
        
        # Simple keyword extraction - split by common separators
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return unique keywords up to max_keywords
        return list(set(keywords))[:max_keywords]