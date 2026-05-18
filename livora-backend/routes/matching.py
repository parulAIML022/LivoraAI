from typing import Annotated

from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, get_current_user, require_roles
from schemas.matching import MatchingResponse
from services.matching_service import (
    get_donor_matches,
    get_matching_for_user,
    get_recipient_matches,
)

router = APIRouter(prefix="/api/matching", tags=["Matching"])

Authenticated = Annotated[CurrentUser, Depends(get_current_user)]
RecipientUser = Annotated[CurrentUser, Depends(require_roles("recipient"))]
DonorUser = Annotated[CurrentUser, Depends(require_roles("donor"))]


@router.get("/me", response_model=MatchingResponse)
def matching_for_current_user(current_user: Authenticated) -> MatchingResponse:
    """Role-aware matches and statistics for the logged-in user."""
    data = get_matching_for_user(current_user.user_id, current_user.role)
    return MatchingResponse(**data)


@router.get("/recipient", response_model=MatchingResponse)
def matching_for_recipient(current_user: RecipientUser) -> MatchingResponse:
    """Recipient: ranked donor match suggestions."""
    data = get_recipient_matches(current_user.user_id)
    return MatchingResponse(**data)


@router.get("/donor", response_model=MatchingResponse)
def matching_for_donor(current_user: DonorUser) -> MatchingResponse:
    """Donor: ranked recipient match suggestions."""
    data = get_donor_matches(current_user.user_id)
    return MatchingResponse(**data)
