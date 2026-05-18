"""Blood group, organ, location, and compatibility scoring for donor–recipient matching."""

from __future__ import annotations

import logging
import os
import re
from typing import Any

logger = logging.getLogger("livora.matching")

# Donor blood type -> recipient blood types they can donate to (simplified)
_BLOOD_DONOR_TO_RECIPIENT: dict[str, set[str]] = {
    "O-": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},
    "O+": {"O+", "A+", "B+", "AB+"},
    "A-": {"A-", "A+", "AB-", "AB+"},
    "A+": {"A+", "AB+"},
    "B-": {"B-", "B+", "AB-", "AB+"},
    "B+": {"B+", "AB+"},
    "AB-": {"AB-", "AB+"},
    "AB+": {"AB+"},
}

_STATUS_ALIASES: dict[str, str] = {
    "approved": "verified",
    "approve": "verified",
}

# Normalized statuses eligible for matching (after normalize_profile_status)
_MATCHABLE_DONOR_NORMALIZED = frozenset({"verified", "active"})
_MATCHABLE_RECIPIENT_NORMALIZED = frozenset({"pending", "verified", "active"})

_NEARBY_KM_THRESHOLD = 50.0

# Longest token first for phrase detection (e.g. bone marrow before marrow)
_ORGAN_TOKENS_ORDERED: tuple[str, ...] = (
    "bone marrow",
    "kidney",
    "liver",
    "heart",
    "pancreas",
    "cornea",
    "intestine",
    "lung",
    "lungs",
)

_ORGAN_ALIASES: dict[str, str] = {
    "kidneys": "kidney",
    "hearts": "heart",
    "lungs": "lung",
    "livers": "liver",
    "pancreases": "pancreas",
    "corneas": "cornea",
    "intestines": "intestine",
    "bonemarrow": "bone marrow",
    "bone-marrow": "bone marrow",
}

_CANONICAL_ORGANS = frozenset(
    {
        "kidney",
        "liver",
        "heart",
        "lung",
        "pancreas",
        "cornea",
        "intestine",
        "bone marrow",
    }
)

_ABO_TYPES = ("AB", "A", "B", "O")

_RH_NEGATIVE = re.compile(r"(NEGATIVE|NEG|-\s*VE|-VE|^\-)", re.IGNORECASE)
_RH_POSITIVE = re.compile(r"(POSITIVE|POS|\+\s*VE|\+VE|^\+)", re.IGNORECASE)

_ORGAN_NOISE_WORDS = re.compile(
    r"\b(transplant|transplants|donation|donations|graft|grafts|organ|organs)\b",
    re.IGNORECASE,
)


def matching_debug_enabled() -> bool:
    """TEMPORARY: set MATCHING_DEBUG=false to disable verbose match logs."""
    return os.getenv("MATCHING_DEBUG", "true").lower() in ("1", "true", "yes", "on")


def _log_match_debug(message: str, *args: Any) -> None:
    if matching_debug_enabled():
        logger.info("[matching] " + message, *args)


def _detect_rh_factor(remainder: str) -> str | None:
    if not remainder:
        return None
    token = remainder.strip().upper()
    if token in ("+", "-"):
        return token
    if _RH_NEGATIVE.search(token):
        return "-"
    if _RH_POSITIVE.search(token):
        return "+"
    return None


def normalize_profile_status(status: str | None) -> str:
    if not status:
        return ""
    normalized = str(status).strip().lower()
    return _STATUS_ALIASES.get(normalized, normalized)


def is_matchable_donor_status(status: str | None) -> bool:
    if not status:
        return False
    raw = str(status).strip().lower()
    if raw in ("verified", "active", "approved"):
        return True
    return normalize_profile_status(status) in _MATCHABLE_DONOR_NORMALIZED


def is_matchable_recipient_status(status: str | None) -> bool:
    if not status:
        return False
    raw = str(status).strip().lower()
    if raw in ("pending", "verified", "active", "approved"):
        return True
    return normalize_profile_status(status) in _MATCHABLE_RECIPIENT_NORMALIZED


def normalize_blood_group(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    text = (
        text.replace("＋", "+")
        .replace("−", "-")
        .replace("–", "-")
        .replace("—", "-")
    )
    text = text.upper().replace("RH", "")
    text = re.sub(r"\s+", "", text)

    # Common typo: zero instead of letter O
    if text.startswith("0"):
        text = "O" + text[1:]

    if text in _BLOOD_DONOR_TO_RECIPIENT:
        return text

    abo: str | None = None
    remainder = text
    for abo_type in _ABO_TYPES:
        if text.startswith(abo_type):
            abo = abo_type
            remainder = text[len(abo_type) :]
            break
        if text == abo_type:
            abo = abo_type
            remainder = ""
            break

    if not abo:
        return None

    rh = _detect_rh_factor(remainder.strip())
    if rh is None:
        return None

    canonical = f"{abo}{rh}"
    if canonical in _BLOOD_DONOR_TO_RECIPIENT:
        return canonical
    return None


def _coerce_organ_strings(value: Any) -> list[str]:
    """Accept list, comma-separated string, or single organ value from MongoDB."""
    if value is None:
        return []
    if isinstance(value, str):
        parts = re.split(r"[,;/|]", value)
        return [p.strip() for p in parts if p and p.strip()]
    if isinstance(value, (list, tuple)):
        items: list[str] = []
        for entry in value:
            items.extend(_coerce_organ_strings(entry))
        return items
    return [str(value).strip()] if str(value).strip() else []


def normalize_organ(name: str | None) -> str | None:
    if name is None:
        return None
    raw = str(name).strip()
    if not raw:
        return None

    slug = raw.lower()
    slug = _ORGAN_NOISE_WORDS.sub(" ", slug)
    slug = re.sub(r"[_\-]+", " ", slug)
    slug = re.sub(r"\s+", " ", slug).strip()

    if not slug:
        return None

    if slug in _ORGAN_ALIASES:
        return _ORGAN_ALIASES[slug]
    if slug in _CANONICAL_ORGANS:
        return slug

    for token in _ORGAN_TOKENS_ORDERED:
        pattern = rf"\b{re.escape(token)}\b"
        if re.search(pattern, slug) or slug == token:
            canonical = _ORGAN_ALIASES.get(token, token)
            if canonical == "lungs":
                return "lung"
            if canonical in _CANONICAL_ORGANS:
                return canonical

    if slug.endswith("s"):
        singular = slug[:-1]
        if singular in _CANONICAL_ORGANS:
            return singular
        if singular in _ORGAN_ALIASES:
            return _ORGAN_ALIASES[singular]

    return None


def collect_donor_organs(donor: dict[str, Any]) -> list[str]:
    organs: list[str] = []
    seen: set[str] = set()

    for raw in _coerce_organ_strings(donor.get("organs")):
        normalized = normalize_organ(raw)
        if normalized and normalized not in seen:
            seen.add(normalized)
            organs.append(normalized)

    # Legacy single-organ field from older payloads
    for key in ("organType", "organ"):
        for raw in _coerce_organ_strings(donor.get(key)):
            normalized = normalize_organ(raw)
            if normalized and normalized not in seen:
                seen.add(normalized)
                organs.append(normalized)

    return organs


def collect_recipient_organs(recipient: dict[str, Any]) -> list[str]:
    organs: list[str] = []
    seen: set[str] = set()

    for raw in _coerce_organ_strings(recipient.get("organs")):
        normalized = normalize_organ(raw)
        if normalized and normalized not in seen:
            seen.add(normalized)
            organs.append(normalized)

    for raw in _coerce_organ_strings(recipient.get("organNeeded")):
        normalized = normalize_organ(raw)
        if normalized and normalized not in seen:
            seen.add(normalized)
            organs.append(normalized)

    for key in ("organType", "organ"):
        for raw in _coerce_organ_strings(recipient.get(key)):
            normalized = normalize_organ(raw)
            if normalized and normalized not in seen:
                seen.add(normalized)
                organs.append(normalized)

    return organs


def organs_overlap(donor_organs: list[str], recipient_organs: list[str]) -> bool:
    donor_set: set[str] = set()
    recipient_set: set[str] = set()
    for raw in donor_organs:
        normalized = normalize_organ(raw)
        if normalized:
            donor_set.add(normalized)
    for raw in recipient_organs:
        normalized = normalize_organ(raw)
        if normalized:
            recipient_set.add(normalized)
    if not donor_set or not recipient_set:
        return False
    if donor_set & recipient_set:
        return True
    for d in donor_set:
        for r in recipient_set:
            if d in r or r in d:
                return True
    return False


def blood_compatible(donor_blood: str | None, recipient_blood: str | None) -> bool:
    donor = normalize_blood_group(donor_blood)
    recipient = normalize_blood_group(recipient_blood)
    if not donor or not recipient:
        return False
    if donor == recipient:
        return True
    return recipient in _BLOOD_DONOR_TO_RECIPIENT.get(donor, set())


def explain_match_rejection(
    *,
    donor: dict[str, Any],
    recipient: dict[str, Any],
) -> str | None:
    """Return human-readable rejection reason, or None if pair is compatible."""
    donor_status = donor.get("status")
    if not is_matchable_donor_status(donor_status):
        return f"donor status not matchable: {donor_status!r}"

    recipient_status = recipient.get("status")
    if not is_matchable_recipient_status(recipient_status):
        return f"recipient status not matchable: {recipient_status!r}"

    donor_organs = collect_donor_organs(donor)
    recipient_organs = collect_recipient_organs(recipient)
    if not donor_organs:
        return "donor has no normalized organs"
    if not recipient_organs:
        return "recipient has no normalized organs (organs/organNeeded)"
    if not organs_overlap(donor_organs, recipient_organs):
        return (
            f"no organ overlap (donor={donor_organs}, recipient={recipient_organs})"
        )

    donor_blood = normalize_blood_group(donor.get("bloodGroup"))
    recipient_blood = normalize_blood_group(recipient.get("bloodGroup"))
    if not donor_blood:
        return f"donor blood group invalid: {donor.get('bloodGroup')!r}"
    if not recipient_blood:
        return f"recipient blood group invalid: {recipient.get('bloodGroup')!r}"
    if not blood_compatible(donor.get("bloodGroup"), recipient.get("bloodGroup")):
        return (
            f"blood incompatible (donor={donor_blood}, recipient={recipient_blood})"
        )

    return None


def compute_compatibility_score(
    *,
    donor: dict[str, Any],
    recipient: dict[str, Any],
    donor_user_name: str = "Donor",
) -> int | None:
    if explain_match_rejection(donor=donor, recipient=recipient) is not None:
        return None

    score = 70.0

    distance_km = estimate_distance_km(donor.get("address"), recipient.get("address"))
    if distance_km <= 10:
        score += 20
    elif distance_km <= _NEARBY_KM_THRESHOLD:
        score += 14
    elif distance_km <= 150:
        score += 8
    else:
        score += 3

    donor_status = normalize_profile_status(donor.get("status"))
    if donor_status == "active":
        score += 6
    elif donor_status == "verified":
        score += 4

    if normalize_profile_status(recipient.get("status")) == "active":
        score += 4

    return min(100, int(round(score)))


def evaluate_match_pair(
    *,
    donor: dict[str, Any],
    recipient: dict[str, Any],
    donor_label: str = "",
    recipient_label: str = "",
) -> tuple[int | None, str | None]:
    """Returns (score, rejection_reason). rejection_reason is None when matched."""
    donor_organs = collect_donor_organs(donor)
    recipient_organs = collect_recipient_organs(recipient)
    donor_blood = normalize_blood_group(donor.get("bloodGroup"))
    recipient_blood = normalize_blood_group(recipient.get("bloodGroup"))

    rejection = explain_match_rejection(donor=donor, recipient=recipient)
    if rejection:
        _log_match_debug(
            "SKIP donor=%s recipient=%s | status(d)=%s status(r)=%s | "
            "blood(d)=%s blood(r)=%s | organs(d)=%s organs(r)=%s | reason=%s",
            donor_label or donor.get("userId"),
            recipient_label or recipient.get("userId"),
            donor.get("status"),
            recipient.get("status"),
            donor_blood,
            recipient_blood,
            donor_organs,
            recipient_organs,
            rejection,
        )
        return None, rejection

    score = compute_compatibility_score(donor=donor, recipient=recipient)
    _log_match_debug(
        "MATCH donor=%s recipient=%s | blood=%s/%s | organs=%s | score=%s",
        donor_label or donor.get("userId"),
        recipient_label or recipient.get("userId"),
        donor_blood,
        recipient_blood,
        list(set(donor_organs) & set(recipient_organs)),
        score,
    )
    return score, None


def extract_location(address: str | None) -> str:
    if not address or not address.strip():
        return "Unknown"
    parts = [p.strip() for p in address.split(",") if p.strip()]
    return parts[0] if parts else address.strip()


def estimate_distance_km(address_a: str | None, address_b: str | None) -> float:
    loc_a = extract_location(address_a).lower()
    loc_b = extract_location(address_b).lower()
    if loc_a == "unknown" or loc_b == "unknown":
        return 250.0
    if loc_a == loc_b:
        return 5.0
    if loc_a in loc_b or loc_b in loc_a:
        return 18.0
    return 120.0


def format_distance(km: float) -> str:
    if km < 1:
        return f"{int(km * 1000)} m"
    if km < 10:
        return f"{km:.1f} km"
    return f"{int(round(km))} km"


def recipient_urgency(recipient_status: str) -> str:
    status = normalize_profile_status(recipient_status)
    if status == "active":
        return "urgent"
    if status == "verified":
        return "normal"
    return "low"


def is_nearby(distance_km: float) -> bool:
    return distance_km <= _NEARBY_KM_THRESHOLD
