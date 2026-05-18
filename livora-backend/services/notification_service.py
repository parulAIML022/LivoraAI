from bson import ObjectId
from fastapi import HTTPException, status

from database.connection import get_notifications_collection
from models.notification import notification_document, serialize_notification


def create_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: str,
    metadata: dict | None = None,
) -> dict:
    doc = notification_document(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        metadata=metadata,
    )
    result = get_notifications_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_notification(doc)


def list_notifications(user_id: str, limit: int = 20) -> dict:
    cursor = (
        get_notifications_collection()
        .find({"userId": user_id})
        .sort("createdAt", -1)
        .limit(limit)
    )
    items = [serialize_notification(doc) for doc in cursor]
    unread = get_unread_count(user_id)
    return {"items": items, "unreadCount": unread}


def get_unread_count(user_id: str) -> int:
    return get_notifications_collection().count_documents(
        {"userId": user_id, "read": False}
    )


def mark_notification_read(user_id: str, notification_id: str) -> dict:
    try:
        oid = ObjectId(notification_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification id",
        ) from exc

    doc = get_notifications_collection().find_one({"_id": oid, "userId": user_id})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    get_notifications_collection().update_one({"_id": oid}, {"$set": {"read": True}})
    doc["read"] = True
    return serialize_notification(doc)


def mark_all_read(user_id: str) -> dict:
    result = get_notifications_collection().update_many(
        {"userId": user_id, "read": False},
        {"$set": {"read": True}},
    )
    return {"marked": result.modified_count}
