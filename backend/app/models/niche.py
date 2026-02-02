"""
Niche Model - Core entity for discovered niches
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Niche(Base):
    __tablename__ = "niches"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    keywords = Column(JSON)  # List of related keywords
    category = Column(String(100), index=True)
    
    # Scoring
    overall_score = Column(Float, default=0.0, index=True)
    trend_score = Column(Float, default=0.0)
    competition_score = Column(Float, default=0.0)
    monetization_score = Column(Float, default=0.0)
    audience_score = Column(Float, default=0.0)
    content_opportunity_score = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    
    # Discovery Information
    discovered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    discovery_source = Column(String(100))  # youtube, tiktok, reddit, etc.
    discovery_method = Column(String(100))  # trending, search, recommendation
    
    # Metadata
    additional_data = Column(JSON)  # Flexible field for source-specific data
    
    # Relationships
    metrics = relationship("Metric", back_populates="niche", cascade="all, delete-orphan")
    trends = relationship("Trend", back_populates="niche", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Niche(id={self.id}, name='{self.name}', score={self.overall_score})>"
    
    @property
    def is_high_potential(self) -> bool:
        """Check if niche has high potential (score >= 90)"""
        return self.overall_score >= 90.0
    
    @property
    def score_breakdown(self) -> dict:
        """Get breakdown of all scores"""
        return {
            "overall": self.overall_score,
            "trend": self.trend_score,
            "competition": self.competition_score,
            "monetization": self.monetization_score,
            "audience": self.audience_score,
            "content_opportunity": self.content_opportunity_score
        }