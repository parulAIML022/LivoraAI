from datetime import datetime, timezone


def notification_document(
    *,
    user_id: str,
    title: str,
    message: str,
    notification_type: str,
    metadata: dict | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "userId": user_id,
        "title": title,
        "message": message,
        "type": notification_type,
        "metadata": metadata or {},
        "read": False,
        "createdAt": now,
    }


def serialize_notification(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "userId": doc["userId"],
        "title": doc["title"],
        "message": doc["message"],
        "type": doc.get("type", "general"),
        "metadata": doc.get("metadata", {}),
        "read": doc.get("read", False),
        "createdAt": doc["createdAt"].isoformat(),
    }
