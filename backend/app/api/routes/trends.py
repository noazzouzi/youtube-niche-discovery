"""
Trends API Routes
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.core.database import get_async_session
from app.models.trend import Trend
from app.schemas.trend import TrendCreate, TrendUpdate, TrendResponse, TrendListResponse

router = APIRouter()

@router.get("/", response_model=TrendListResponse)
async def get_trends(
    niche_id: Optional[int] = Query(None),
    period_type: Optional[str] = Query(None),
    days_back: int = Query(30, ge=1, le=365),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session)
):
    """Get trends with filtering options"""
    query = select(Trend)
    
    conditions = []
    if niche_id:
        conditions.append(Trend.niche_id == niche_id)
    if period_type:
        conditions.append(Trend.period_type == period_type)
    
    # Filter by date range
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    conditions.append(Trend.timestamp >= cutoff_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(desc(Trend.timestamp)).limit(limit)
    
    result = await session.execute(query)
    trends = result.scalars().all()
    
    return TrendListResponse(
        trends=trends,
        total=len(trends)
    )

@router.get("/{niche_id}/timeline")
async def get_niche_timeline(
    niche_id: int,
    period_type: str = Query("daily"),
    days_back: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_async_session)
):
    """Get timeline of trends for a specific niche"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    
    query = select(Trend).where(
        and_(
            Trend.niche_id == niche_id,
            Trend.period_type == period_type,
            Trend.timestamp >= cutoff_date
        )
    ).order_by(Trend.timestamp)
    
    result = await session.execute(query)
    trends = result.scalars().all()
    
    return {
        "niche_id": niche_id,
        "period_type": period_type,
        "timeline": [
            {
                "timestamp": trend.timestamp,
                "overall_score": trend.overall_score,
                "score_change": trend.score_change,
                "trend_direction": trend.trend_direction,
                "momentum": trend.momentum
            }
            for trend in trends
        ]
    }

@router.post("/", response_model=TrendResponse)
async def create_trend(
    trend_data: TrendCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new trend entry"""
    trend = Trend(**trend_data.dict())
    session.add(trend)
    await session.commit()
    await session.refresh(trend)
    
    return trend