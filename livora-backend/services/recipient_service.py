from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from database.connection import get_recipients_collection, get_users_collection
from models.recipient import recipient_document, serialize_recipient
from schemas.recipient import RecipientUpdateRequest


def _ensure_recipient_profile(user_id: str) -> dict:
    recipients = get_recipients_collection()
    recipient = recipients.find_one({"userId": user_id})
    if recipient:
        return recipient

    user = get_users_collection().find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "recipient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a recipient",
        )
    recipients.insert_one(recipient_document(user_id=user_id))
    recipient = recipients.find_one({"userId": user_id})
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recipient profile",
        )
    return recipient


def get_recipient_profile(user_id: str) -> dict:
    return serialize_recipient(_ensure_recipient_profile(user_id))


def update_recipient_profile(user_id: str, payload: RecipientUpdateRequest) -> dict:
    recipients = get_recipients_collection()
    _ensure_recipient_profile(user_id)

    update_data = payload.model_dump(exclude_unset=True)
    if "organs" in update_data and update_data["organs"]:
        update_data["organs"] = [o.strip().lower() for o in update_data["organs"] if o.strip()]
    if update_data.get("organNeeded") and not update_data.get("organs"):
        update_data["organs"] = [update_data["organNeeded"].strip().lower()]

    if not update_data:
        return serialize_recipient(_ensure_recipient_profile(user_id))

    update_data["updatedAt"] = datetime.now(timezone.utc)
    recipients.update_one({"userId": user_id}, {"$set": update_data})
    return serialize_recipient(_ensure_recipient_profile(user_id))
