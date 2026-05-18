from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from database.connection import get_recipients_collection, get_users_collection
from models.recipient import recipient_document, serialize_recipient
from schemas.recipient import (
    RecipientStatus,
    RecipientUpdateRequest,
    VALID_RECIPIENT_STATUSES,
)


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


def update_recipient_status_by_user_id(
    target_user_id: str,
    new_status: RecipientStatus,
) -> dict:
    """Hospital/admin: set recipient approval status."""
    if new_status not in VALID_RECIPIENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status value",
        )

    recipients = get_recipients_collection()
    recipient = recipients.find_one({"userId": target_user_id})
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient profile not found",
        )

    old_status = recipient.get("status", "pending")
    recipients.update_one(
        {"userId": target_user_id},
        {
            "$set": {
                "status": new_status,
                "updatedAt": datetime.now(timezone.utc),
            }
        },
    )

    if old_status != new_status:
        _notify_recipient_status_change(target_user_id, new_status)

    return serialize_recipient(recipients.find_one({"userId": target_user_id}))


def _notify_recipient_status_change(user_id: str, new_status: str) -> None:
    from services.notification_service import create_notification

    messages = {
        "verified": (
            "Recipient profile verified",
            "Your recipient profile has been verified. AI matching is now enabled.",
            "recipient_verified",
        ),
        "active": (
            "Active transplant request",
            "Your recipient profile is active. Urgent matches may be prioritized.",
            "match_found",
        ),
        "inactive": (
            "Recipient account inactive",
            "Your recipient profile has been marked inactive.",
            "status_update",
        ),
        "pending": (
            "Recipient review pending",
            "Your profile is awaiting hospital approval.",
            "status_update",
        ),
    }
    title, message, ntype = messages.get(
        new_status,
        (
            "Recipient status updated",
            f"Your recipient status is now {new_status}.",
            "status_update",
        ),
    )
    create_notification(user_id, title, message, ntype, {"status": new_status})
