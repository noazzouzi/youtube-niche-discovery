"""
API Routes Package
"""

from fastapi import APIRouter
from .niches import router as niches_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(niches_router, prefix="/niches", tags=["niches"])

__all__ = ["api_router"]