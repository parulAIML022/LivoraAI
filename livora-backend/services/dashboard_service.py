from datetime import datetime, timedelta, timezone

from database.connection import (
    get_donors_collection,
    get_recipients_collection,
    get_users_collection,
)
from services.matching_service import get_donor_matches, get_recipient_matches


def _recent_approvals_count(days: int = 7) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    donors = get_donors_collection().count_documents(
        {"status": {"$in": ["verified", "active"]}, "updatedAt": {"$gte": since}}
    )
    recipients = get_recipients_collection().count_documents(
        {"status": {"$in": ["verified", "active"]}, "updatedAt": {"$gte": since}}
    )
    return donors + recipients


def get_dashboard_stats(user_id: str, role: str) -> dict:
    if role == "recipient":
        data = get_recipient_matches(user_id, limit=100)
        stats = data["stats"]
        return {
            "totalMatches": stats["totalMatches"],
            "pendingRequests": stats.get("pendingRequests", 0),
            "verifiedDonors": stats.get("verifiedDonors", 0),
            "nearbyDonors": stats.get("nearbyMatches", 0),
            "averageCompatibility": stats.get("averageCompatibility", 0),
            "activeRecipientRequests": stats.get("activeRecipientRequests", 0),
        }

    if role == "donor":
        data = get_donor_matches(user_id, limit=100)
        stats = data["stats"]
        return {
            "totalMatches": stats["totalMatches"],
            "nearbyDonors": stats.get("nearbyMatches", 0),
            "averageCompatibility": stats.get("averageCompatibility", 0),
            "pendingRequests": get_donors_collection().count_documents(
                {"userId": user_id, "status": "pending"}
            ),
            "verifiedDonors": 1
            if get_donors_collection().find_one(
                {"userId": user_id, "status": {"$in": ["verified", "active"]}}
            )
            else 0,
        }

    if role == "hospital":
        return _hospital_stats()

    if role == "admin":
        return _admin_stats()

    return {}


def _hospital_stats() -> dict:
    pending_donors = get_donors_collection().count_documents({"status": "pending"})
    pending_recipients = get_recipients_collection().count_documents({"status": "pending"})
    active_transplants = get_recipients_collection().count_documents(
        {"status": "active"}
    )
    verified_donors = get_donors_collection().count_documents(
        {"status": {"$in": ["verified", "active"]}}
    )

    return {
        "pendingDonorVerifications": pending_donors,
        "pendingRecipientApprovals": pending_recipients,
        "recentApprovals": _recent_approvals_count(),
        "activeTransplantRequests": active_transplants,
        "verifiedDonors": verified_donors,
        "totalMatches": _count_platform_matches(),
    }


def _admin_stats() -> dict:
    hospital_stats = _hospital_stats()
    total_users = get_users_collection().count_documents({})
    total_donors = get_donors_collection().count_documents({})
    total_recipients = get_recipients_collection().count_documents({})
    total_hospitals = get_users_collection().count_documents({"role": "hospital"})
    flagged = get_users_collection().count_documents({"flagged": True})

    return {
        **hospital_stats,
        "totalUsers": total_users,
        "totalDonors": total_donors,
        "totalRecipients": total_recipients,
        "totalHospitals": total_hospitals,
        "flaggedAccounts": flagged,
        "pendingRequests": hospital_stats["pendingDonorVerifications"]
        + hospital_stats["pendingRecipientApprovals"],
    }


def _count_platform_matches() -> int:
    """Approximate total compatible pairs on the platform."""
    from services.matching_service import _get_staff_matching_overview

    return _get_staff_matching_overview()["stats"]["totalMatches"]
