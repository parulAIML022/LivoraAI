from bson import ObjectId

from database.connection import (
    get_donors_collection,
    get_recipients_collection,
    get_users_collection,
)
from models.donor import serialize_donor
from models.recipient import serialize_recipient


def _serialize_user_summary(user: dict, profile: dict | None, role: str) -> dict:
    base = {
        "userId": str(user["_id"]),
        "fullName": user.get("fullName", ""),
        "email": user.get("email", ""),
        "role": role,
        "createdAt": user.get("createdAt").isoformat() if user.get("createdAt") else None,
    }
    if not profile:
        return {**base, "profileStatus": None, "bloodGroup": None, "organs": [], "organNeeded": None}

    if role == "donor":
        serialized = serialize_donor(profile)
        return {
            **base,
            "profileStatus": serialized["status"],
            "bloodGroup": serialized.get("bloodGroup"),
            "organs": serialized.get("organs", []),
            "organNeeded": None,
        }

    serialized = serialize_recipient(profile)
    return {
        **base,
        "profileStatus": serialized["status"],
        "bloodGroup": serialized.get("bloodGroup"),
        "organs": serialized.get("organs", []),
        "organNeeded": serialized.get("organNeeded"),
    }


def list_pending_users(status_filter: str | None = "pending") -> dict:
    donor_query = {"status": status_filter} if status_filter else {}
    recipient_query = {"status": status_filter} if status_filter else {}

    donor_profiles = list(get_donors_collection().find(donor_query))
    recipient_profiles = list(get_recipients_collection().find(recipient_query))

    donor_user_ids = [ObjectId(d["userId"]) for d in donor_profiles]
    recipient_user_ids = [ObjectId(r["userId"]) for r in recipient_profiles]

    donor_users = {
        str(u["_id"]): u
        for u in get_users_collection().find({"_id": {"$in": donor_user_ids}})
    }
    recipient_users = {
        str(u["_id"]): u
        for u in get_users_collection().find({"_id": {"$in": recipient_user_ids}})
    }

    donors = []
    for profile in donor_profiles:
        user = donor_users.get(profile["userId"])
        if user:
            donors.append(_serialize_user_summary(user, profile, "donor"))

    recipients = []
    for profile in recipient_profiles:
        user = recipient_users.get(profile["userId"])
        if user:
            recipients.append(_serialize_user_summary(user, profile, "recipient"))

    return {"donors": donors, "recipients": recipients}
