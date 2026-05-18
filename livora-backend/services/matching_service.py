"""Simple manual donor–recipient matching (blood group + organ + verified status)."""

from __future__ import annotations

from bson import ObjectId
from fastapi import HTTPException, status

from database.connection import (
    get_donors_collection,
    get_recipients_collection,
    get_users_collection,
)
from services.donor_service import _ensure_donor_profile
from services.recipient_service import _ensure_recipient_profile

COMPATIBILITY_SCORE = 95
NO_MATCHES_MESSAGE = "No compatible donors found."


def _user_map(user_ids: list[str]) -> dict[str, dict]:
    if not user_ids:
        return {}
    oids = []
    for uid in user_ids:
        try:
            oids.append(ObjectId(uid))
        except Exception:
            continue
    if not oids:
        return {}
    users = get_users_collection().find({"_id": {"$in": oids}})
    return {str(u["_id"]): u for u in users}


def _fetch_verified_donors() -> list[dict]:
    """All donors with status exactly 'verified' (case-insensitive)."""
    return [
        d
        for d in get_donors_collection().find({})
        if str(d.get("status", "")).lower().strip() == "verified"
    ]


def _donor_matches_recipient(donor: dict, recipient: dict) -> str | None:
    """
    Return matching organ slug if donor fits recipient; otherwise None.
    """
    recipient_blood = str(recipient.get("bloodGroup") or "").lower().strip()
    organ_needed = str(recipient.get("organNeeded") or "").lower().strip()
    if not recipient_blood or not organ_needed:
        return None

    donor_blood = str(donor.get("bloodGroup") or "").lower().strip()
    if donor_blood != recipient_blood:
        return None

    if str(donor.get("status") or "").lower().strip() != "verified":
        return None

    donor_organs = [
        str(organ).lower().strip()
        for organ in (donor.get("organs") or [])
        if organ
    ]
    if organ_needed not in donor_organs:
        return None

    return organ_needed


def build_recipient_matches(user_id: str, limit: int = 50) -> dict:
    """Manual filter: same blood, organ in donor list, donor verified."""
    recipient = _ensure_recipient_profile(user_id)
    verified_donors = _fetch_verified_donors()
    users = _user_map([d["userId"] for d in verified_donors])

    matches: list[dict] = []
    for donor in verified_donors:
        if donor.get("userId") == user_id:
            continue

        matching_organ = _donor_matches_recipient(donor, recipient)
        if not matching_organ:
            continue

        user = users.get(donor["userId"], {})
        matches.append(
            {
                "donorName": user.get("fullName", "Donor"),
                "bloodGroup": donor.get("bloodGroup"),
                "organ": matching_organ,
                "location": donor.get("address") or "Unknown",
                "status": donor.get("status", "verified"),
                "compatibilityScore": COMPATIBILITY_SCORE,
            }
        )

    if limit > 0:
        matches = matches[:limit]

    count = len(matches)
    stats = {
        "totalMatches": count,
        "nearbyMatches": count,
        "averageCompatibility": COMPATIBILITY_SCORE if count else 0,
        "newMatchesThisWeek": 0,
        "pendingRequests": get_recipients_collection().count_documents({"status": "pending"}),
        "verifiedDonors": len(verified_donors),
        "activeRecipientRequests": get_recipients_collection().count_documents(
            {"status": {"$in": ["verified", "active"]}}
        ),
    }

    return {
        "matches": matches,
        "message": None if matches else NO_MATCHES_MESSAGE,
        "stats": stats,
        "urgentAlert": None,
    }


def get_recipient_matches(user_id: str, limit: int = 20) -> dict:
    return build_recipient_matches(user_id, limit=limit)


def get_matching_for_user(user_id: str, role: str) -> dict:
    if role == "recipient":
        return build_recipient_matches(user_id)
    if role == "donor":
        return {
            "matches": [],
            "message": NO_MATCHES_MESSAGE,
            "stats": {
                "totalMatches": 0,
                "nearbyMatches": 0,
                "averageCompatibility": 0,
                "newMatchesThisWeek": 0,
            },
            "urgentAlert": None,
        }
    if role in ("hospital", "admin"):
        return _staff_matching_summary()
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Matching not available for this role",
    )


def get_donor_matches(user_id: str, limit: int = 20) -> dict:
    _ensure_donor_profile(user_id)
    return {
        "matches": [],
        "message": NO_MATCHES_MESSAGE,
        "stats": {
            "totalMatches": 0,
            "nearbyMatches": 0,
            "averageCompatibility": 0,
            "newMatchesThisWeek": 0,
        },
        "urgentAlert": None,
    }


def _staff_matching_summary() -> dict:
    """Hospital/admin: count compatible pairs using the same manual rules."""
    verified_donors = _fetch_verified_donors()
    recipients = list(get_recipients_collection().find({}))
    pair_count = 0

    for recipient in recipients:
        for donor in verified_donors:
            if _donor_matches_recipient(donor, recipient):
                pair_count += 1

    return {
        "matches": [],
        "message": None if pair_count else NO_MATCHES_MESSAGE,
        "stats": {
            "totalMatches": pair_count,
            "nearbyMatches": 0,
            "averageCompatibility": COMPATIBILITY_SCORE if pair_count else 0,
            "newMatchesThisWeek": 0,
            "verifiedDonors": len(verified_donors),
            "activeRecipientRequests": len(recipients),
            "pendingRequests": get_donors_collection().count_documents({"status": "pending"})
            + get_recipients_collection().count_documents({"status": "pending"}),
        },
        "urgentAlert": None,
    }


def count_platform_manual_matches() -> int:
    return _staff_matching_summary()["stats"]["totalMatches"]
