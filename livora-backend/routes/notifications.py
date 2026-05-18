from typing import Annotated

from fastapi import APIRouter, Depends, Query

from middleware.auth import CurrentUser, get_current_user
from schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from services.notification_service import (
    get_unread_count,
    list_notifications,
    mark_all_read,
    mark_notification_read,
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

Authenticated = Annotated[CurrentUser, Depends(get_current_user)]


@router.get("", response_model=NotificationListResponse)
def get_notifications(
    current_user: Authenticated,
    limit: int = Query(20, ge=1, le=50),
) -> NotificationListResponse:
    data = list_notifications(current_user.user_id, limit=limit)
    return NotificationListResponse(**data)


@router.get("/unread-count", response_model=UnreadCountResponse)
def unread_count(current_user: Authenticated) -> UnreadCountResponse:
    return UnreadCountResponse(count=get_unread_count(current_user.user_id))


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(
    notification_id: str,
    current_user: Authenticated,
) -> NotificationResponse:
    data = mark_notification_read(current_user.user_id, notification_id)
    return NotificationResponse(**data)


@router.patch("/read-all")
def mark_all_notifications_read(current_user: Authenticated) -> dict:
    return mark_all_read(current_user.user_id)
