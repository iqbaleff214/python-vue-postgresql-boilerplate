from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.search.schemas import SearchResponse
from app.search.service import run_search

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Max results per provider"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Global command-palette search endpoint.

    Returns results grouped by category. Each provider in the registry
    decides what data to expose based on the current user's role.
    """
    groups = await run_search(db, current_user, q.strip(), limit)
    return SearchResponse(query=q, groups=groups)
