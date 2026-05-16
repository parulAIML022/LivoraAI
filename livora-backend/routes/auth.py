from typing import Annotated

from fastapi import APIRouter, Depends

from middleware.auth import CurrentUser, get_current_user
from schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from services.auth_service import get_user_by_id, login_user, signup_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest) -> TokenResponse:
    """Register a new user and return JWT."""
    return signup_user(payload)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate and return JWT."""
    return login_user(payload)


@router.post("/logout")
def logout(
    _current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> dict:
    """Client should discard token; endpoint confirms session was valid."""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[CurrentUser, Depends(get_current_user)]) -> UserResponse:
    """Return the authenticated user's profile."""
    data = get_user_by_id(current_user.user_id)
    return UserResponse(**data)
