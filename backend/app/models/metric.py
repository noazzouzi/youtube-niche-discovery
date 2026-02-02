"""
Metric Model - Track specific metrics for niches from different sources
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Metric(Base):
    __tablename__ = "metrics"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    niche_id = Column(Integer, ForeignKey("niches.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    
    # Metric Information
    metric_type = Column(String(100), nullable=False, index=True)  # views, engagement, competition, etc.
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    normalized_value = Column(Float)  # Normalized to 0-100 scale
    
    # Context
    period = Column(String(50))  # daily, weekly, monthly, yearly
    date_range_start = Column(DateTime(timezone=True))
    date_range_end = Column(DateTime(timezone=True))
    
    # Metadata
    collection_method = Column(String(100))  # api, scraping, manual
    confidence_score = Column(Float, default=100.0)  # 0-100, how confident we are in this data
    sample_size = Column(Integer)  # For metrics based on samples
    
    # Raw and Additional Data
    raw_data = Column(JSON)  # Store original data from source
    additional_metrics = Column(JSON)  # Store related metrics as key-value pairs
    
    # Timestamps
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    niche = relationship("Niche", back_populates="metrics")
    source = relationship("Source", back_populates="metrics")
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('ix_metrics_niche_source', 'niche_id', 'source_id'),
        Index('ix_metrics_type_collected', 'metric_type', 'collected_at'),
        Index('ix_metrics_niche_type_period', 'niche_id', 'metric_type', 'period'),
    )
    
    def __repr__(self):
        return f"<Metric(id={self.id}, niche_id={self.niche_id}, type='{self.metric_type}', value={self.value})>"
    
    @property
    def is_recent(self) -> bool:
        """Check if metric was collected recently (within 24 hours)"""
        from datetime import datetime, timedelta
        return self.collected_at and (datetime.utcnow() - self.collected_at) <= timedelta(hours=24)
    
    @property
    def age_in_hours(self) -> float:
        """Get age of metric in hours"""
        from datetime import datetime
        if not self.collected_at:
            return float('inf')
        return (datetime.utcnow() - self.collected_at).total_seconds() / 3600
    
    def normalize_value(self, min_val: float = 0, max_val: float = 100) -> float:
        """Normalize the value to a 0-100 scale"""
        if max_val == min_val:
            return 50.0  # Default middle value if no range
        
        normalized = ((self.value - min_val) / (max_val - min_val)) * 100
        return max(0, min(100, normalized))
    
    @classmethod
    def get_metric_types(cls):
        """Get common metric types"""
        return [
            # Trend Metrics
            "search_volume",
            "growth_rate", 
            "trending_score",
            "viral_potential",
            
            # Competition Metrics
            "competition_level",
            "content_saturation",
            "creator_count",
            "average_views",
            
            # Monetization Metrics
            "cpm_estimate",
            "ad_revenue_potential",
            "brand_deal_potential",
            "product_sales_potential",
            
            # Audience Metrics
            "audience_size",
            "engagement_rate",
            "audience_growth",
            "demographic_data",
            
            # Content Metrics
            "content_gap_score",
            "upload_frequency",
            "content_quality_score",
            "trending_keywords"
        ]