from typing import Annotated

from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, require_roles
from schemas.recipient import RecipientResponse, RecipientUpdateRequest
from services.recipient_service import get_recipient_profile, update_recipient_profile

router = APIRouter(prefix="/api/recipients", tags=["Recipients"])

RecipientUser = Annotated[CurrentUser, Depends(require_roles("recipient"))]


@router.get("/me", response_model=RecipientResponse)
def get_my_recipient_profile(current_user: RecipientUser) -> RecipientResponse:
    """Fetch the authenticated recipient's profile (creates empty profile if needed)."""
    data = get_recipient_profile(current_user.user_id)
    return RecipientResponse(**data)


@router.put("/me", response_model=RecipientResponse)
def update_my_recipient_profile(
    payload: RecipientUpdateRequest,
    current_user: RecipientUser,
) -> RecipientResponse:
    """Create or update recipient medical profile."""
    data = update_recipient_profile(current_user.user_id, payload)
    return RecipientResponse(**data)
