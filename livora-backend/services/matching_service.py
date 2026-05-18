from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import HTTPException, status

from database.connection import (
    get_donors_collection,
    get_recipients_collection,
    get_users_collection,
)
from services.donor_service import _ensure_donor_profile
from services.recipient_service import _ensure_recipient_profile
from utils.matching_engine import (
    _log_match_debug,
    collect_donor_organs,
    collect_recipient_organs,
    estimate_distance_km,
    evaluate_match_pair,
    extract_location,
    format_distance,
    is_matchable_donor_status,
    is_matchable_recipient_status,
    is_nearby,
    matching_debug_enabled,
    normalize_organ,
    normalize_profile_status,
    recipient_urgency,
)


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


def _display_name(users: dict[str, dict], user_id: str, fallback: str) -> str:
    return users.get(user_id, {}).get("fullName") or fallback


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if not parts:
        return "?"
    return "".join(p[0].upper() for p in parts[:2])


def _organ_label_for_match(donor: dict, recipient: dict) -> str | None:
    donor_set = set(collect_donor_organs(donor))
    recipient_set = set(collect_recipient_organs(recipient))
    overlap = donor_set & recipient_set
    if overlap:
        return sorted(overlap)[0]
    if recipient_set:
        return sorted(recipient_set)[0]
    donor_list = collect_donor_organs(donor)
    return donor_list[0] if donor_list else normalize_organ(recipient.get("organNeeded"))


def _build_match_entry(
    *,
    match_id: str,
    counterpart_user_id: str,
    display_name: str,
    counterpart_role: str,
    blood_group: str | None,
    compatibility: int,
    location: str,
    distance_km: float,
    urgency: str,
    organ_type: str | None,
    verification_status: str,
) -> dict:
    return {
        "id": match_id,
        "counterpartUserId": counterpart_user_id,
        "displayName": display_name,
        "initials": _initials(display_name),
        "bloodGroup": blood_group,
        "compatibility": compatibility,
        "location": location,
        "distance": format_distance(distance_km),
        "distanceKm": distance_km,
        "urgency": urgency,
        "organType": organ_type,
        "verificationStatus": verification_status,
        "role": counterpart_role,
    }


def _compute_stats(matches: list[dict], *, extra: dict | None = None) -> dict:
    compatibilities = [m["compatibility"] for m in matches]
    nearby = sum(1 for m in matches if is_nearby(m["distanceKm"]))
    avg = int(round(sum(compatibilities) / len(compatibilities))) if compatibilities else 0

    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    new_this_week = 0
    for m in matches:
        created = m.get("_createdAt")
        if created and created >= week_ago:
            new_this_week += 1

    stats = {
        "totalMatches": len(matches),
        "nearbyMatches": nearby,
        "averageCompatibility": avg,
        "newMatchesThisWeek": new_this_week,
        "pendingRequests": 0,
        "verifiedDonors": 0,
        "activeRecipientRequests": 0,
    }
    if extra:
        stats.update(extra)
    return stats


def _urgent_alert(matches: list[dict]) -> dict | None:
    urgent = [m for m in matches if m.get("urgency") == "urgent"]
    if not urgent:
        return None
    best = max(urgent, key=lambda m: m["compatibility"])
    loc = best.get("location", "nearby")
    return {
        "message": f"Urgent match available in {loc}",
        "location": loc,
        "matchId": best.get("id"),
    }


def get_recipient_matches(user_id: str, limit: int = 20) -> dict:
    recipient = _ensure_recipient_profile(user_id)
    all_donors = list(get_donors_collection().find({}))
    user_ids = [d["userId"] for d in all_donors]
    users = _user_map(user_ids)

    if matching_debug_enabled():
        _log_match_debug(
            "recipient_matches start recipient=%s (%s) | donors_in_db=%s",
            _display_name(users, user_id, user_id),
            user_id,
            len(all_donors),
        )

    matches: list[dict] = []
    skipped_status = 0

    for donor in all_donors:
        if donor.get("userId") == user_id:
            continue

        if not is_matchable_donor_status(donor.get("status")):
            skipped_status += 1
            continue

        donor_name = _display_name(users, donor["userId"], "Donor")
        score, _rejection = evaluate_match_pair(
            donor=donor,
            recipient=recipient,
            donor_label=donor_name,
            recipient_label=_display_name(users, user_id, "Recipient"),
        )
        if score is None:
            continue

        distance_km = estimate_distance_km(donor.get("address"), recipient.get("address"))
        entry = _build_match_entry(
            match_id=f"{user_id}:{donor['userId']}",
            counterpart_user_id=donor["userId"],
            display_name=donor_name,
            counterpart_role="donor",
            blood_group=donor.get("bloodGroup"),
            compatibility=score,
            location=extract_location(donor.get("address")),
            distance_km=distance_km,
            urgency=recipient_urgency(recipient.get("status", "pending")),
            organ_type=_organ_label_for_match(donor, recipient),
            verification_status=str(donor.get("status", "pending")),
        )
        entry["_createdAt"] = donor.get("updatedAt")
        matches.append(entry)

    matches.sort(key=lambda m: (-m["compatibility"], m["distanceKm"]))
    total_found = len(matches)
    matches = matches[:limit]

    verified_donors = sum(
        1 for d in all_donors if is_matchable_donor_status(d.get("status"))
    )
    active_requests = sum(
        1
        for r in get_recipients_collection().find({})
        if normalize_profile_status(r.get("status")) == "active"
    )

    stats = _compute_stats(
        matches,
        extra={
            "nearbyMatches": sum(1 for m in matches if is_nearby(m["distanceKm"])),
            "verifiedDonors": verified_donors,
            "activeRecipientRequests": active_requests,
            "pendingRequests": get_recipients_collection().count_documents(
                {"status": "pending"}
            ),
        },
    )

    for m in matches:
        m.pop("_createdAt", None)

    _log_match_debug(
        "recipient_matches done recipient=%s | donors_scanned=%s skipped_status=%s "
        "| matches_found=%s | returned=%s",
        user_id,
        len(all_donors),
        skipped_status,
        total_found,
        len(matches),
    )

    return {
        "matches": matches,
        "stats": stats,
        "urgentAlert": _urgent_alert(matches),
    }


def get_donor_matches(user_id: str, limit: int = 20) -> dict:
    donor = _ensure_donor_profile(user_id)
    all_recipients = list(get_recipients_collection().find({}))
    user_ids = [r["userId"] for r in all_recipients]
    users = _user_map(user_ids)

    if matching_debug_enabled():
        _log_match_debug(
            "donor_matches start donor=%s | recipients_in_db=%s",
            user_id,
            len(all_recipients),
        )

    matches: list[dict] = []

    for recipient in all_recipients:
        if recipient.get("userId") == user_id:
            continue
        if not is_matchable_recipient_status(recipient.get("status")):
            continue

        recipient_name = _display_name(users, recipient["userId"], "Recipient")
        score, _rejection = evaluate_match_pair(
            donor=donor,
            recipient=recipient,
            donor_label=_display_name(users, user_id, "Donor"),
            recipient_label=recipient_name,
        )
        if score is None:
            continue

        distance_km = estimate_distance_km(donor.get("address"), recipient.get("address"))
        entry = _build_match_entry(
            match_id=f"{donor['userId']}:{recipient['userId']}",
            counterpart_user_id=recipient["userId"],
            display_name=recipient_name,
            counterpart_role="recipient",
            blood_group=recipient.get("bloodGroup"),
            compatibility=score,
            location=extract_location(recipient.get("address")),
            distance_km=distance_km,
            urgency=recipient_urgency(recipient.get("status", "pending")),
            organ_type=_organ_label_for_match(donor, recipient),
            verification_status=str(recipient.get("status", "pending")),
        )
        entry["_createdAt"] = recipient.get("updatedAt")
        matches.append(entry)

    matches.sort(key=lambda m: (-m["compatibility"], m["distanceKm"]))
    total_found = len(matches)
    matches = matches[:limit]

    for m in matches:
        m.pop("_createdAt", None)

    _log_match_debug(
        "donor_matches done donor=%s | matches_found=%s | returned=%s",
        user_id,
        total_found,
        len(matches),
    )

    stats = _compute_stats(matches)
    return {
        "matches": matches,
        "stats": stats,
        "urgentAlert": _urgent_alert(matches),
    }


def get_matching_for_user(user_id: str, role: str) -> dict:
    if role == "recipient":
        return get_recipient_matches(user_id)
    if role == "donor":
        return get_donor_matches(user_id)
    if role in ("hospital", "admin"):
        return _get_staff_matching_overview()
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Matching not available for this role",
    )


def _get_staff_matching_overview() -> dict:
    all_donors = list(get_donors_collection().find({}))
    donors = [d for d in all_donors if is_matchable_donor_status(d.get("status"))]
    all_recipients = list(get_recipients_collection().find({}))
    recipients = [r for r in all_recipients if is_matchable_recipient_status(r.get("status"))]

    all_user_ids = [d["userId"] for d in donors] + [r["userId"] for r in recipients]
    users = _user_map(all_user_ids)

    matches: list[dict] = []
    for recipient in recipients:
        for donor in donors:
            score, _ = evaluate_match_pair(
                donor=donor,
                recipient=recipient,
                donor_label=_display_name(users, donor["userId"], "Donor"),
                recipient_label=_display_name(users, recipient["userId"], "Recipient"),
            )
            if score is None:
                continue
            donor_user = users.get(donor["userId"], {})
            recipient_user = users.get(recipient["userId"], {})
            distance_km = estimate_distance_km(donor.get("address"), recipient.get("address"))
            matches.append(
                _build_match_entry(
                    match_id=f"{donor['userId']}:{recipient['userId']}",
                    counterpart_user_id=recipient["userId"],
                    display_name=(
                        f"{donor_user.get('fullName', 'Donor')} → "
                        f"{recipient_user.get('fullName', 'Recipient')}"
                    ),
                    counterpart_role="recipient",
                    blood_group=donor.get("bloodGroup"),
                    compatibility=score,
                    location=extract_location(recipient.get("address")),
                    distance_km=distance_km,
                    urgency=recipient_urgency(recipient.get("status", "pending")),
                    organ_type=_organ_label_for_match(donor, recipient),
                    verification_status=str(donor.get("status", "pending")),
                )
            )

    matches.sort(key=lambda m: (-m["compatibility"], m["distanceKm"]))
    top = matches[:10]
    stats = _compute_stats(
        matches,
        extra={
            "verifiedDonors": len(donors),
            "activeRecipientRequests": len(recipients),
            "pendingRequests": sum(
                1
                for d in all_donors
                if not is_matchable_donor_status(d.get("status"))
            )
            + sum(
                1
                for r in all_recipients
                if not is_matchable_recipient_status(r.get("status"))
            ),
        },
    )
    return {"matches": top, "stats": stats, "urgentAlert": _urgent_alert(top)}
