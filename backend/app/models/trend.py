"""
Trend Model - Track historical trends and changes for niches
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Trend(Base):
    __tablename__ = "trends"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    niche_id = Column(Integer, ForeignKey("niches.id"), nullable=False, index=True)
    
    # Time Information
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    
    # Score Tracking
    overall_score = Column(Float, nullable=False)
    trend_score = Column(Float)
    competition_score = Column(Float)
    monetization_score = Column(Float)
    audience_score = Column(Float)
    content_opportunity_score = Column(Float)
    
    # Score Changes (compared to previous period)
    score_change = Column(Float)  # Change in overall score
    trend_change = Column(Float)
    competition_change = Column(Float)
    monetization_change = Column(Float)
    audience_change = Column(Float)
    content_change = Column(Float)
    
    # Trend Indicators
    trend_direction = Column(String(10))  # up, down, stable
    momentum = Column(Float)  # Rate of change
    volatility = Column(Float)  # How much the score fluctuates
    
    # Key Metrics Snapshot
    search_volume = Column(Integer)
    competition_level = Column(Float)
    engagement_rate = Column(Float)
    content_volume = Column(Integer)  # Number of pieces of content
    
    # Events and Context
    significant_events = Column(JSON)  # List of events that may have influenced the trend
    external_factors = Column(JSON)  # External factors (holidays, news, etc.)
    notes = Column(Text)
    
    # Data Quality
    data_completeness = Column(Float, default=100.0)  # Percentage of expected data points collected
    confidence_level = Column(Float, default=100.0)  # Confidence in the trend calculation
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    niche = relationship("Niche", back_populates="trends")
    
    # Indexes for efficient time-series queries
    __table_args__ = (
        Index('ix_trends_niche_timestamp', 'niche_id', 'timestamp'),
        Index('ix_trends_period_timestamp', 'period_type', 'timestamp'),
        Index('ix_trends_niche_period', 'niche_id', 'period_type'),
        Index('ix_trends_score_timestamp', 'overall_score', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Trend(id={self.id}, niche_id={self.niche_id}, score={self.overall_score}, timestamp={self.timestamp})>"
    
    @property
    def is_positive_trend(self) -> bool:
        """Check if trend is positive (score increasing)"""
        return self.score_change is not None and self.score_change > 0
    
    @property
    def is_significant_change(self) -> bool:
        """Check if the score change is significant (>= 5 points)"""
        return self.score_change is not None and abs(self.score_change) >= 5.0
    
    @property
    def trend_summary(self) -> dict:
        """Get a summary of the trend"""
        return {
            "direction": self.trend_direction,
            "momentum": self.momentum,
            "score_change": self.score_change,
            "is_significant": self.is_significant_change,
            "volatility": self.volatility,
            "confidence": self.confidence_level
        }
    
    def calculate_momentum(self, previous_trend: 'Trend' = None) -> float:
        """Calculate momentum based on score changes"""
        if not previous_trend or self.score_change is None:
            return 0.0
        
        # Simple momentum calculation: rate of change acceleration
        prev_change = previous_trend.score_change or 0.0
        current_change = self.score_change
        
        return current_change - prev_change
    
    def classify_trend_strength(self) -> str:
        """Classify the strength of the trend"""
        if not self.score_change:
            return "unknown"
        
        abs_change = abs(self.score_change)
        
        if abs_change >= 20:
            return "very_strong"
        elif abs_change >= 10:
            return "strong"
        elif abs_change >= 5:
            return "moderate"
        elif abs_change >= 2:
            return "weak"
        else:
            return "stable"
    
    @classmethod
    def get_trend_directions(cls):
        """Get possible trend directions"""
        return ["up", "down", "stable", "volatile"]
    
    @classmethod
    def get_period_types(cls):
        """Get possible period types"""
        return ["hourly", "daily", "weekly", "monthly"]