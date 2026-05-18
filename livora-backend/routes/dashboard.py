from typing import Annotated

from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, get_current_user
from schemas.dashboard import DashboardStatsResponse
from services.dashboard_service import get_dashboard_stats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

Authenticated = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("/stats", response_model=DashboardStatsResponse)
def dashboard_stats(current_user: Authenticated) -> DashboardStatsResponse:
    """Role-aware dashboard statistics from MongoDB."""
    data = get_dashboard_stats(current_user.user_id, current_user.role)
    return DashboardStatsResponse(**data)
