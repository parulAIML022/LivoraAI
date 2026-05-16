from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.jwt_handler import decode_access_token

security = HTTPBearer(auto_error=False)


class CurrentUser:
    def __init__(self, user_id: str, role: str, email: str | None = None):
        self.user_id = user_id
        self.role = role
        self.email = email


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("sub")
    role = payload.get("role")
    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return CurrentUser(user_id=str(user_id), role=str(role), email=payload.get("email"))


def require_roles(*allowed_roles: str):
    def role_checker(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' is not allowed for this resource",
            )
        return current_user

    return role_checker
