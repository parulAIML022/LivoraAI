from typing import Annotated

from fastapi import APIRouter, Depends, Query

from middleware.auth import CurrentUser, require_roles
from schemas.dashboard import AdminUserListResponse, DashboardStatsResponse
from services.admin_service import list_pending_users
from services.dashboard_service import get_dashboard_stats

router = APIRouter(prefix="/api/admin", tags=["Admin"])

HospitalOrAdmin = Annotated[
    CurrentUser, Depends(require_roles("hospital", "admin"))
]


@router.get("/stats", response_model=DashboardStatsResponse)
def admin_stats(_actor: HospitalOrAdmin) -> DashboardStatsResponse:
    data = get_dashboard_stats("", "admin")
    return DashboardStatsResponse(**data)


@router.get("/pending", response_model=AdminUserListResponse)
def pending_registrations(
    _actor: HospitalOrAdmin,
    status: str | None = Query("pending", description="Profile status filter"),
) -> AdminUserListResponse:
    data = list_pending_users(status_filter=status)
    return AdminUserListResponse(**data)
