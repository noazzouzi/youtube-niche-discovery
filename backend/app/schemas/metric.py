"""
Metric Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MetricBase(BaseModel):
    metric_type: str = Field(..., max_length=100)
    metric_name: str = Field(..., max_length=255)
    value: float
    period: Optional[str] = Field(None, max_length=50)

class MetricCreate(MetricBase):
    niche_id: int
    source_id: int
    normalized_value: Optional[float] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    collection_method: Optional[str] = Field(None, max_length=100)
    confidence_score: float = Field(100.0, ge=0, le=100)
    sample_size: Optional[int] = None
    raw_data: Optional[Dict[str, Any]] = None
    additional_metrics: Optional[Dict[str, Any]] = None

class MetricUpdate(BaseModel):
    value: Optional[float] = None
    normalized_value: Optional[float] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    raw_data: Optional[Dict[str, Any]] = None
    additional_metrics: Optional[Dict[str, Any]] = None

class MetricResponse(MetricBase):
    id: int
    niche_id: int
    source_id: int
    normalized_value: Optional[float]
    confidence_score: float
    collected_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class MetricListResponse(BaseModel):
    metrics: List[MetricResponse]
    total: int