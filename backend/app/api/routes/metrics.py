"""
Metrics API Routes
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_

from app.core.database import get_async_session
from app.models.metric import Metric
from app.schemas.metric import MetricCreate, MetricUpdate, MetricResponse, MetricListResponse

router = APIRouter()

@router.get("/", response_model=MetricListResponse)
async def get_metrics(
    niche_id: Optional[int] = Query(None),
    source_id: Optional[int] = Query(None),
    metric_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_async_session)
):
    """Get metrics with filtering options"""
    query = select(Metric)
    
    conditions = []
    if niche_id:
        conditions.append(Metric.niche_id == niche_id)
    if source_id:
        conditions.append(Metric.source_id == source_id)
    if metric_type:
        conditions.append(Metric.metric_type == metric_type)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(desc(Metric.collected_at)).limit(limit)
    
    result = await session.execute(query)
    metrics = result.scalars().all()
    
    return MetricListResponse(
        metrics=metrics,
        total=len(metrics)
    )

@router.post("/", response_model=MetricResponse)
async def create_metric(
    metric_data: MetricCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new metric"""
    metric = Metric(**metric_data.dict())
    session.add(metric)
    await session.commit()
    await session.refresh(metric)
    
    return metric

@router.get("/types")
async def get_metric_types():
    """Get available metric types"""
    return {"metric_types": Metric.get_metric_types()}