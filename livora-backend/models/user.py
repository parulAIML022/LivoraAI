from datetime import datetime, timezone

from bson import ObjectId


def user_document(
    *,
    full_name: str,
    email: str,
    hashed_password: str,
    role: str,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "fullName": full_name,
        "email": email.lower(),
        "hashedPassword": hashed_password,
        "role": role,
        "createdAt": now,
        "updatedAt": now,
    }


def serialize_user(doc: dict) -> dict:
    return {
        "userId": str(doc["_id"]),
        "fullName": doc["fullName"],
        "email": doc["email"],
        "role": doc["role"],
        "createdAt": doc["createdAt"].isoformat(),
    }
