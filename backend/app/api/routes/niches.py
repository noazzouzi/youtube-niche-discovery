"""
Niches API Routes - Enhanced with PM Agent Discovery Service
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_, func
from datetime import datetime

from app.core.database import get_async_session
from app.models.niche import Niche
from app.schemas.niche import NicheCreate, NicheUpdate, NicheResponse, NicheListResponse
from app.services.niche_discovery_service import NicheDiscoveryService
from app.services.scoring_service import ScoringService

router = APIRouter()

@router.get("/", response_model=NicheListResponse)
async def get_niches(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    is_active: Optional[bool] = Query(True),
    is_validated: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("overall_score", enum=["overall_score", "discovered_at", "name"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get list of niches with filtering and sorting options
    """
    query = select(Niche)
    
    # Apply filters
    conditions = []
    if is_active is not None:
        conditions.append(Niche.is_active == is_active)
    if is_validated is not None:
        conditions.append(Niche.is_validated == is_validated)
    if category:
        conditions.append(Niche.category == category)
    if min_score is not None:
        conditions.append(Niche.overall_score >= min_score)
    if max_score is not None:
        conditions.append(Niche.overall_score <= max_score)
    if search:
        conditions.append(
            or_(
                Niche.name.ilike(f"%{search}%"),
                Niche.description.ilike(f"%{search}%")
            )
        )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(desc(getattr(Niche, sort_by)))
    else:
        query = query.order_by(getattr(Niche, sort_by))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await session.execute(query)
    niches = result.scalars().all()
    
    # Get total count for pagination
    count_query = select(func.count(Niche.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    count_result = await session.execute(count_query)
    total_count = count_result.scalar()
    
    return NicheListResponse(
        niches=niches,
        total=total_count,
        skip=skip,
        limit=limit
    )

@router.get("/high-potential/", response_model=List[Dict[str, Any]])
async def get_high_potential_niches(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get high-potential niches (90+ score) with full PM Agent analysis
    """
    discovery_service = NicheDiscoveryService(session)
    high_potential = await discovery_service.get_high_potential_niches(limit)
    return high_potential

@router.post("/discover/daily")
async def discover_niches_daily(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Trigger daily niche discovery workflow (PM Agent implementation)
    
    This endpoint:
    1. Discovers 100+ niches from multiple sources
    2. Applies the 100-point scoring algorithm  
    3. Identifies high-potential opportunities
    4. Returns immediate summary, continues processing in background
    """
    discovery_service = NicheDiscoveryService(session)
    
    # Start discovery process in background
    background_tasks.add_task(discovery_service.discover_niches_daily)
    
    return {
        "message": "Daily niche discovery started",
        "status": "processing",
        "target": "100+ niches",
        "algorithm": "PM Agent 100-point scoring",
        "started_at": datetime.utcnow().isoformat()
    }

@router.get("/discover/status")
async def get_discovery_status(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get current discovery status and recent results
    """
    # Get recent discovery stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Count niches discovered today
    today_query = select(func.count(Niche.id)).where(
        and_(
            Niche.discovered_at >= today_start,
            Niche.is_active == True
        )
    )
    today_result = await session.execute(today_query)
    today_count = today_result.scalar()
    
    # Count high-potential niches discovered today
    high_potential_query = select(func.count(Niche.id)).where(
        and_(
            Niche.discovered_at >= today_start,
            Niche.overall_score >= 90.0,
            Niche.is_active == True
        )
    )
    high_potential_result = await session.execute(high_potential_query)
    high_potential_count = high_potential_result.scalar()
    
    # Get latest discoveries
    latest_query = select(Niche).where(
        Niche.is_active == True
    ).order_by(desc(Niche.discovered_at)).limit(10)
    
    latest_result = await session.execute(latest_query)
    latest_niches = latest_result.scalars().all()
    
    return {
        "date": datetime.utcnow().isoformat(),
        "today_stats": {
            "total_discovered": today_count,
            "high_potential": high_potential_count,
            "target_progress": f"{today_count}/100"
        },
        "latest_discoveries": [
            {
                "name": niche.name,
                "score": niche.overall_score,
                "category": niche.category,
                "discovered_at": niche.discovered_at.isoformat()
            } for niche in latest_niches
        ]
    }

@router.get("/{niche_id}/analyze")
async def analyze_niche_deeply(
    niche_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Perform deep analysis of a specific niche using PM Agent algorithm
    
    Returns:
    - Complete score breakdown
    - Latest metrics from all sources
    - Actionable recommendations
    - Historical trends
    """
    discovery_service = NicheDiscoveryService(session)
    analysis = await discovery_service.analyze_niche_deeply(niche_id)
    
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    
    return analysis

@router.post("/{niche_id}/rescore")
async def rescore_niche(
    niche_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Recalculate scores for a specific niche with fresh data
    """
    # Check if niche exists
    query = select(Niche).where(Niche.id == niche_id)
    result = await session.execute(query)
    niche = result.scalar_one_or_none()
    
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    # Rescore using PM algorithm
    scoring_service = ScoringService(session)
    success = await scoring_service.update_niche_scores(niche_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update scores")
    
    # Get updated niche
    await session.refresh(niche)
    
    return {
        "message": "Niche rescored successfully",
        "niche_id": niche_id,
        "new_score": niche.overall_score,
        "updated_at": niche.last_updated.isoformat()
    }

@router.post("/batch/rescore")
async def rescore_all_niches(
    limit: Optional[int] = Query(None, ge=1, le=1000),
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Recalculate scores for all active niches (background process)
    """
    scoring_service = ScoringService(session)
    
    # Start rescoring in background
    background_tasks.add_task(scoring_service.batch_update_scores, limit)
    
    return {
        "message": "Batch rescoring started",
        "status": "processing",
        "limit": limit or "all active niches",
        "started_at": datetime.utcnow().isoformat()
    }

@router.get("/{niche_id}", response_model=NicheResponse)
async def get_niche(
    niche_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get a specific niche by ID"""
    query = select(Niche).where(Niche.id == niche_id)
    result = await session.execute(query)
    niche = result.scalar_one_or_none()
    
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    return niche

@router.post("/", response_model=NicheResponse)
async def create_niche(
    niche_data: NicheCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new niche"""
    # Check if niche with same name already exists
    existing_query = select(Niche).where(Niche.name == niche_data.name)
    existing_result = await session.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Niche with this name already exists")
    
    # Create new niche
    niche = Niche(**niche_data.dict())
    session.add(niche)
    await session.commit()
    await session.refresh(niche)
    
    return niche

@router.put("/{niche_id}", response_model=NicheResponse)
async def update_niche(
    niche_id: int,
    niche_data: NicheUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Update an existing niche"""
    query = select(Niche).where(Niche.id == niche_id)
    result = await session.execute(query)
    niche = result.scalar_one_or_none()
    
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    # Update fields
    update_data = niche_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(niche, field, value)
    
    await session.commit()
    await session.refresh(niche)
    
    return niche

@router.delete("/{niche_id}")
async def delete_niche(
    niche_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a niche (soft delete by setting is_active=False)"""
    query = select(Niche).where(Niche.id == niche_id)
    result = await session.execute(query)
    niche = result.scalar_one_or_none()
    
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    niche.is_active = False
    await session.commit()
    
    return {"message": "Niche deleted successfully"}

@router.get("/{niche_id}/score-breakdown")
async def get_niche_score_breakdown(
    niche_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Get detailed PM Agent score breakdown for a niche"""
    query = select(Niche).where(Niche.id == niche_id)
    result = await session.execute(query)
    niche = result.scalar_one_or_none()
    
    if not niche:
        raise HTTPException(status_code=404, detail="Niche not found")
    
    # Get the complete PM scoring breakdown
    scoring_service = ScoringService(session)
    scores = await scoring_service.calculate_niche_score(niche.id)
    
    return {
        "niche_id": niche.id,
        "niche_name": niche.name,
        "pm_algorithm_breakdown": {
            "overall_score": scores["overall_score"],
            "components": {
                "search_volume": {
                    "score": scores["search_volume_score"],
                    "max_points": 25,
                    "percentage": round((scores["search_volume_score"] / 25) * 100, 1),
                    "description": "Google Trends + YouTube search volume"
                },
                "competition": {
                    "score": scores["competition_score"],
                    "max_points": 25,
                    "percentage": round((scores["competition_score"] / 25) * 100, 1),
                    "description": "Channel saturation + subscriber growth (inverse)"
                },
                "monetization": {
                    "score": scores["monetization_score"],
                    "max_points": 20,
                    "percentage": round((scores["monetization_score"] / 20) * 100, 1),
                    "description": "CPM rates + brand safety"
                },
                "content_availability": {
                    "score": scores["content_availability_score"],
                    "max_points": 15,
                    "percentage": round((scores["content_availability_score"] / 15) * 100, 1),
                    "description": "Reddit + TikTok + news coverage"
                },
                "trend_momentum": {
                    "score": scores["trend_momentum_score"],
                    "max_points": 15,
                    "percentage": round((scores["trend_momentum_score"] / 15) * 100, 1),
                    "description": "12-month growth + social momentum"
                }
            }
        },
        "performance_indicators": {
            "is_high_potential": scores["overall_score"] >= 90,
            "is_viable": scores["overall_score"] >= 50,
            "risk_level": "low" if scores["overall_score"] >= 80 else "medium" if scores["overall_score"] >= 60 else "high",
            "recommendation": "IMMEDIATE ACTION" if scores["overall_score"] >= 90 else "CONSIDER" if scores["overall_score"] >= 70 else "RESEARCH MORE" if scores["overall_score"] >= 50 else "SKIP"
        },
        "last_calculated": datetime.utcnow().isoformat()
    }

@router.get("/categories/", response_model=List[str])
async def get_categories(
    session: AsyncSession = Depends(get_async_session)
):
    """Get all unique categories"""
    query = select(Niche.category).where(
        and_(Niche.category.isnot(None), Niche.is_active == True)
    ).distinct()
    
    result = await session.execute(query)
    categories = [cat for cat in result.scalars().all() if cat]
    
    return sorted(categories)

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get dashboard statistics for the PM Agent Niche Discovery Engine
    """
    # Total niches
    total_query = select(func.count(Niche.id)).where(Niche.is_active == True)
    total_result = await session.execute(total_query)
    total_niches = total_result.scalar()
    
    # High potential (90+)
    high_potential_query = select(func.count(Niche.id)).where(
        and_(Niche.overall_score >= 90, Niche.is_active == True)
    )
    high_potential_result = await session.execute(high_potential_query)
    high_potential_count = high_potential_result.scalar()
    
    # Medium potential (70-89)
    medium_potential_query = select(func.count(Niche.id)).where(
        and_(
            Niche.overall_score >= 70,
            Niche.overall_score < 90,
            Niche.is_active == True
        )
    )
    medium_potential_result = await session.execute(medium_potential_query)
    medium_potential_count = medium_potential_result.scalar()
    
    # Categories distribution
    category_query = select(Niche.category, func.count(Niche.id)).where(
        Niche.is_active == True
    ).group_by(Niche.category).order_by(desc(func.count(Niche.id)))
    
    category_result = await session.execute(category_query)
    categories = [{"category": cat, "count": count} for cat, count in category_result.all()]
    
    # Recent discoveries (last 24h)
    yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    recent_query = select(func.count(Niche.id)).where(
        and_(Niche.discovered_at >= yesterday, Niche.is_active == True)
    )
    recent_result = await session.execute(recent_query)
    recent_discoveries = recent_result.scalar()
    
    # Average score
    avg_score_query = select(func.avg(Niche.overall_score)).where(Niche.is_active == True)
    avg_score_result = await session.execute(avg_score_query)
    avg_score = avg_score_result.scalar() or 0
    
    return {
        "summary": {
            "total_niches": total_niches,
            "high_potential": high_potential_count,
            "medium_potential": medium_potential_count,
            "recent_discoveries_24h": recent_discoveries,
            "average_score": round(float(avg_score), 2)
        },
        "performance_metrics": {
            "high_potential_rate": round((high_potential_count / max(total_niches, 1)) * 100, 1),
            "discovery_target_progress": f"{recent_discoveries}/100",
            "algorithm_effectiveness": round(float(avg_score), 1)
        },
        "category_distribution": categories[:10],  # Top 10 categories
        "generated_at": datetime.utcnow().isoformat()
    }