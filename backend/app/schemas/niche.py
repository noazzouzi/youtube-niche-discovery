"""
Niche Pydantic Schemas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

# Base schema with common fields
class NicheBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)

# Schema for creating a niche
class NicheCreate(NicheBase):
    discovery_source: Optional[str] = Field(None, max_length=100)
    discovery_method: Optional[str] = Field(None, max_length=100)
    additional_data: Optional[Dict[str, Any]] = None
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None and len(v) > 50:
            raise ValueError('Maximum 50 keywords allowed')
        return v

# Schema for updating a niche
class NicheUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = Field(None, max_length=100)
    overall_score: Optional[float] = Field(None, ge=0, le=100)
    trend_score: Optional[float] = Field(None, ge=0, le=100)
    competition_score: Optional[float] = Field(None, ge=0, le=100)
    monetization_score: Optional[float] = Field(None, ge=0, le=100)
    audience_score: Optional[float] = Field(None, ge=0, le=100)
    content_opportunity_score: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_validated: Optional[bool] = None
    validation_notes: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v is not None and len(v) > 50:
            raise ValueError('Maximum 50 keywords allowed')
        return v

# Schema for niche response
class NicheResponse(NicheBase):
    id: int
    overall_score: float
    trend_score: float
    competition_score: float
    monetization_score: float
    audience_score: float
    content_opportunity_score: float
    is_active: bool
    is_validated: bool
    validation_notes: Optional[str]
    discovered_at: datetime
    last_updated: datetime
    discovery_source: Optional[str]
    discovery_method: Optional[str]
    additional_data: Optional[Dict[str, Any]]
    
    # Computed properties
    is_high_potential: bool
    score_breakdown: Dict[str, float]
    
    class Config:
        from_attributes = True
        
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model_type) -> None:
            schema["properties"]["is_high_potential"] = {
                "type": "boolean",
                "description": "Whether the niche has high potential (score >= 90)"
            }
            schema["properties"]["score_breakdown"] = {
                "type": "object",
                "description": "Breakdown of all scoring components"
            }

# Schema for listing niches with pagination
class NicheListResponse(BaseModel):
    niches: List[NicheResponse]
    total: int
    skip: int
    limit: int
    
    @property
    def has_next(self) -> bool:
        """Check if there are more results"""
        return (self.skip + self.limit) < self.total
    
    @property
    def has_previous(self) -> bool:
        """Check if there are previous results"""
        return self.skip > 0

# Schema for niche summary (lightweight version)
class NicheSummary(BaseModel):
    id: int
    name: str
    category: Optional[str]
    overall_score: float
    is_active: bool
    is_validated: bool
    discovered_at: datetime
    
    class Config:
        from_attributes = True

# Schema for niche statistics
class NicheStats(BaseModel):
    total_niches: int
    active_niches: int
    validated_niches: int
    high_potential_niches: int
    average_score: float
    categories_count: int
    recent_discoveries: int  # Discovered in last 24 hours
    
    class Config:
        from_attributes = True

# Schema for niche search filters
class NicheFilters(BaseModel):
    category: Optional[str] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    max_score: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = True
    is_validated: Optional[bool] = None
    search: Optional[str] = None
    discovery_source: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None