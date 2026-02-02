"""
Trend Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class TrendBase(BaseModel):
    timestamp: datetime
    period_type: str = Field(..., max_length=20)
    overall_score: float = Field(..., ge=0, le=100)

class TrendCreate(TrendBase):
    niche_id: int
    trend_score: Optional[float] = Field(None, ge=0, le=100)
    competition_score: Optional[float] = Field(None, ge=0, le=100)
    monetization_score: Optional[float] = Field(None, ge=0, le=100)
    audience_score: Optional[float] = Field(None, ge=0, le=100)
    content_opportunity_score: Optional[float] = Field(None, ge=0, le=100)
    score_change: Optional[float] = None
    trend_direction: Optional[str] = Field(None, max_length=10)
    momentum: Optional[float] = None
    volatility: Optional[float] = None
    significant_events: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None

class TrendUpdate(BaseModel):
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    trend_score: Optional[float] = Field(None, ge=0, le=100)
    competition_score: Optional[float] = Field(None, ge=0, le=100)
    monetization_score: Optional[float] = Field(None, ge=0, le=100)
    audience_score: Optional[float] = Field(None, ge=0, le=100)
    content_opportunity_score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None

class TrendResponse(TrendBase):
    id: int
    niche_id: int
    score_change: Optional[float]
    trend_direction: Optional[str]
    momentum: Optional[float]
    volatility: Optional[float]
    confidence_level: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class TrendListResponse(BaseModel):
    trends: List[TrendResponse]
    total: int