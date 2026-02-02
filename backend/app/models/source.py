"""
Source Model - Track data sources and their configurations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Source(Base):
    __tablename__ = "sources"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(100), unique=True, nullable=False, index=True)  # youtube, tiktok, reddit
    display_name = Column(String(255))
    description = Column(Text)
    
    # Configuration
    base_url = Column(String(500))
    api_endpoint = Column(String(500))
    requires_auth = Column(Boolean, default=False)
    auth_type = Column(String(50))  # api_key, oauth, basic, etc.
    
    # Rate Limiting
    requests_per_minute = Column(Integer, default=60)
    requests_per_hour = Column(Integer, default=1000)
    requests_per_day = Column(Integer, default=10000)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_available = Column(Boolean, default=True)
    last_successful_request = Column(DateTime(timezone=True))
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Performance Metrics
    average_response_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    
    # Scoring Weights (how much this source contributes to overall niche score)
    trend_weight = Column(Float, default=1.0)
    competition_weight = Column(Float, default=1.0)
    monetization_weight = Column(Float, default=1.0)
    audience_weight = Column(Float, default=1.0)
    content_weight = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Configuration and Metadata
    scraping_config = Column(JSON)  # Source-specific scraping configuration
    api_config = Column(JSON)  # API-specific configuration
    metadata = Column(JSON)  # Additional metadata
    
    # Relationships
    metrics = relationship("Metric", back_populates="source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    @property
    def is_healthy(self) -> bool:
        """Check if source is healthy (low error rate)"""
        if self.total_requests == 0:
            return True
        return self.success_rate >= 80.0 and self.error_count < 10
    
    @property
    def requests_remaining_today(self) -> int:
        """Calculate remaining requests for today (simplified)"""
        # This would need actual tracking implementation
        return max(0, self.requests_per_day - self.total_requests)
    
    def update_performance_metrics(self, success: bool, response_time: float):
        """Update performance metrics after a request"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.error_count = max(0, self.error_count - 1)  # Decrease error count on success
        else:
            self.error_count += 1
        
        self.success_rate = (self.successful_requests / self.total_requests) * 100
        
        # Update average response time (simple moving average)
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) / 
                self.total_requests
            )