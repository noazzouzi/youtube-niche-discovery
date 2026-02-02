"""
Sources API Routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse, SourceListResponse

router = APIRouter()

@router.get("/", response_model=SourceListResponse)
async def get_sources(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all sources"""
    query = select(Source)
    result = await session.execute(query)
    sources = result.scalars().all()
    
    return SourceListResponse(
        sources=sources,
        total=len(sources)
    )

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific source by ID"""
    query = select(Source).where(Source.id == source_id)
    result = await session.execute(query)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return source

@router.post("/", response_model=SourceResponse)
async def create_source(
    source_data: SourceCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new source"""
    # Check if source with same name already exists
    existing_query = select(Source).where(Source.name == source_data.name)
    existing_result = await session.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Source with this name already exists")
    
    # Create new source
    source = Source(**source_data.dict())
    session.add(source)
    await session.commit()
    await session.refresh(source)
    
    return source

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_data: SourceUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update an existing source"""
    query = select(Source).where(Source.id == source_id)
    result = await session.execute(query)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Update fields
    update_data = source_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(source, field, value)
    
    await session.commit()
    await session.refresh(source)
    
    return source

@router.get("/{source_id}/health")
async def get_source_health(
    source_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get health status of a source"""
    query = select(Source).where(Source.id == source_id)
    result = await session.execute(query)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    return {
        "source_id": source.id,
        "name": source.name,
        "is_healthy": source.is_healthy,
        "success_rate": source.success_rate,
        "average_response_time": source.average_response_time,
        "total_requests": source.total_requests,
        "error_count": source.error_count,
        "last_successful_request": source.last_successful_request,
        "requests_remaining_today": source.requests_remaining_today
    }