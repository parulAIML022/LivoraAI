from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile

from middleware.auth import CurrentUser, require_roles
from schemas.donor import (
    DonorResponse,
    DonorStatusUpdateRequest,
    DonorUpdateRequest,
)
from services.donor_service import (
    get_donor_profile,
    update_donor_profile,
    update_donor_status_by_user_id,
    upload_donor_document,
)

router = APIRouter(prefix="/api/donors", tags=["Donors"])

DonorUser = Annotated[CurrentUser, Depends(require_roles("donor"))]
HospitalOrAdmin = Annotated[
    CurrentUser, Depends(require_roles("hospital", "admin"))
]


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.get("/me", response_model=DonorResponse)
def get_my_donor_profile(
    request: Request,
    current_user: DonorUser,
) -> DonorResponse:
    """Fetch the authenticated donor's profile."""
    data = get_donor_profile(current_user.user_id, base_url=_base_url(request))
    return DonorResponse(**data)


@router.put("/me", response_model=DonorResponse)
def update_my_donor_profile(
    request: Request,
    payload: DonorUpdateRequest,
    current_user: DonorUser,
) -> DonorResponse:
    """Create or update donor medical profile (status is always server-managed)."""
    data = update_donor_profile(
        current_user.user_id,
        payload,
        base_url=_base_url(request),
    )
    return DonorResponse(**data)


@router.post("/me/documents", response_model=DonorResponse)
async def upload_document(
    request: Request,
    current_user: DonorUser,
    file: UploadFile = File(...),
) -> DonorResponse:
    """Upload PDF/JPG/PNG medical document."""
    data = upload_donor_document(
        current_user.user_id,
        file,
        base_url=_base_url(request),
    )
    return DonorResponse(**data)


@router.patch("/{user_id}/status", response_model=DonorResponse)
def set_donor_status(
    user_id: str,
    payload: DonorStatusUpdateRequest,
    request: Request,
    _actor: HospitalOrAdmin,
) -> DonorResponse:
    """Hospital/admin: update a donor's approval status."""
    data = update_donor_status_by_user_id(
        user_id,
        payload.status,
        base_url=_base_url(request),
    )
    return DonorResponse(**data)
