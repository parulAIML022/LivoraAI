from typing import Annotated

from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, require_roles
from schemas.recipient import (
    RecipientResponse,
    RecipientStatusUpdateRequest,
    RecipientUpdateRequest,
)
from services.recipient_service import (
    get_recipient_profile,
    update_recipient_profile,
    update_recipient_status_by_user_id,
)

router = APIRouter(prefix="/api/recipients", tags=["Recipients"])

RecipientUser = Annotated[CurrentUser, Depends(require_roles("recipient"))]
HospitalOrAdmin = Annotated[
    CurrentUser, Depends(require_roles("hospital", "admin"))
]


@router.get("/me", response_model=RecipientResponse)
def get_my_recipient_profile(current_user: RecipientUser) -> RecipientResponse:
    """Fetch the authenticated recipient's profile."""
    data = get_recipient_profile(current_user.user_id)
    return RecipientResponse(**data)


@router.put("/me", response_model=RecipientResponse)
def update_my_recipient_profile(
    payload: RecipientUpdateRequest,
    current_user: RecipientUser,
) -> RecipientResponse:
    """Create or update recipient medical profile (status is always server-managed)."""
    data = update_recipient_profile(current_user.user_id, payload)
    return RecipientResponse(**data)


@router.patch("/{user_id}/status", response_model=RecipientResponse)
def set_recipient_status(
    user_id: str,
    payload: RecipientStatusUpdateRequest,
    _actor: HospitalOrAdmin,
) -> RecipientResponse:
    """Hospital/admin: update a recipient's approval status."""
    data = update_recipient_status_by_user_id(user_id, payload.status)
    return RecipientResponse(**data)
