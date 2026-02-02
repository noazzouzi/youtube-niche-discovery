"""
Source Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    base_url: Optional[str] = Field(None, max_length=500)

class SourceCreate(SourceBase):
    api_endpoint: Optional[str] = Field(None, max_length=500)
    requires_auth: bool = False
    auth_type: Optional[str] = Field(None, max_length=50)
    requests_per_minute: int = Field(60, gt=0)
    requests_per_hour: int = Field(1000, gt=0)
    requests_per_day: int = Field(10000, gt=0)
    scraping_config: Optional[Dict[str, Any]] = None
    api_config: Optional[Dict[str, Any]] = None

class SourceUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    base_url: Optional[str] = Field(None, max_length=500)
    api_endpoint: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    requests_per_minute: Optional[int] = Field(None, gt=0)
    requests_per_hour: Optional[int] = Field(None, gt=0)
    requests_per_day: Optional[int] = Field(None, gt=0)
    scraping_config: Optional[Dict[str, Any]] = None
    api_config: Optional[Dict[str, Any]] = None

class SourceResponse(SourceBase):
    id: int
    is_active: bool
    is_available: bool
    success_rate: float
    average_response_time: float
    total_requests: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SourceListResponse(BaseModel):
    sources: List[SourceResponse]
    total: int