from datetime import datetime, timezone


def _organs_list(organ_type: str | None, organs: list[str] | None) -> list[str]:
    if organs:
        return [o.strip().lower() for o in organs if o.strip()]
    if organ_type:
        return [organ_type.strip().lower()]
    return []


def donor_document(
    *,
    user_id: str,
    blood_group: str | None = None,
    organ_type: str | None = None,
    organs: list[str] | None = None,
    age: int | None = None,
    gender: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    medical_history: str | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "userId": user_id,
        "bloodGroup": blood_group,
        "organs": _organs_list(organ_type, organs),
        "age": age,
        "gender": gender,
        "phone": phone,
        "address": address,
        "medicalHistory": medical_history or "",
        "documents": [],
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
    }


PROFILE_FIELDS = (
    "bloodGroup",
    "organs",
    "age",
    "gender",
    "phone",
    "address",
    "medicalHistory",
)


def calculate_profile_completion(doc: dict) -> int:
    filled = 0
    total = len(PROFILE_FIELDS) + 1  # +1 for at least one document
    for field in PROFILE_FIELDS:
        value = doc.get(field)
        if field == "organs" and isinstance(value, list) and len(value) > 0:
            filled += 1
        elif field == "medicalHistory" and value:
            filled += 1
        elif value not in (None, "", []):
            filled += 1
    if doc.get("documents"):
        filled += 1
    return min(100, round((filled / total) * 100))


def serialize_donor(doc: dict, base_url: str = "") -> dict:
    documents = []
    for d in doc.get("documents", []):
        url = d.get("url", "")
        if url and not url.startswith("http") and base_url:
            url = f"{base_url.rstrip('/')}{url}"
        documents.append(
            {
                "filename": d.get("filename", ""),
                "originalName": d.get("originalName", ""),
                "contentType": d.get("contentType", ""),
                "uploadedAt": d.get("uploadedAt", ""),
                "url": url or d.get("url", ""),
            }
        )
    return {
        "id": str(doc["_id"]),
        "userId": doc["userId"],
        "bloodGroup": doc.get("bloodGroup"),
        "organs": doc.get("organs", []),
        "age": doc.get("age"),
        "gender": doc.get("gender"),
        "phone": doc.get("phone"),
        "address": doc.get("address"),
        "medicalHistory": doc.get("medicalHistory"),
        "documents": documents,
        "status": doc.get("status", "pending"),
        "profileCompletion": calculate_profile_completion(doc),
        "createdAt": doc["createdAt"].isoformat(),
        "updatedAt": doc["updatedAt"].isoformat(),
    }
