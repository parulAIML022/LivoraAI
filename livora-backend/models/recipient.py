from datetime import datetime, timezone


def recipient_document(
    *,
    user_id: str,
    organ_needed: str | None = None,
    organs: list[str] | None = None,
    blood_group: str | None = None,
    age: int | None = None,
    gender: str | None = None,
    medical_history: str | None = None,
    phone: str | None = None,
    address: str | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    organ_list: list[str] = []
    if organs:
        organ_list = [o.strip().lower() for o in organs if o.strip()]
    elif organ_needed:
        organ_list = [organ_needed.strip().lower()]

    return {
        "userId": user_id,
        "organNeeded": organ_needed or (organ_list[0] if organ_list else None),
        "organs": organ_list,
        "bloodGroup": blood_group,
        "age": age,
        "gender": gender,
        "medicalHistory": medical_history or "",
        "phone": phone,
        "address": address,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
    }


PROFILE_FIELDS = (
    "organNeeded",
    "organs",
    "bloodGroup",
    "age",
    "gender",
    "phone",
    "address",
    "medicalHistory",
)


def calculate_profile_completion(doc: dict) -> int:
    filled = 0
    total = len(PROFILE_FIELDS)
    for field in PROFILE_FIELDS:
        value = doc.get(field)
        if field == "organs" and isinstance(value, list) and len(value) > 0:
            filled += 1
        elif field == "medicalHistory" and value:
            filled += 1
        elif value not in (None, "", []):
            filled += 1
    return min(100, round((filled / total) * 100)) if total else 0


def serialize_recipient(doc: dict) -> dict:
    organs = doc.get("organs", [])
    return {
        "id": str(doc["_id"]),
        "userId": doc["userId"],
        "organNeeded": doc.get("organNeeded"),
        "organs": organs,
        "bloodGroup": doc.get("bloodGroup"),
        "age": doc.get("age"),
        "gender": doc.get("gender"),
        "phone": doc.get("phone"),
        "address": doc.get("address"),
        "medicalHistory": doc.get("medicalHistory"),
        "status": doc.get("status", "pending"),
        "profileCompletion": calculate_profile_completion(doc),
        "createdAt": doc["createdAt"].isoformat(),
        "updatedAt": doc["updatedAt"].isoformat(),
    }
