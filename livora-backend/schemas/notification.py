from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    userId: str
    title: str
    message: str
    type: str
    metadata: dict = {}
    read: bool
    createdAt: str


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unreadCount: int


class UnreadCountResponse(BaseModel):
    count: int
