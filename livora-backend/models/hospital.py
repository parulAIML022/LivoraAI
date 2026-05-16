from datetime import datetime, timezone


def hospital_document(
    *,
    user_id: str,
    hospital_name: str | None = None,
    address: str | None = None,
    phone: str | None = None,
    icu_capacity: int | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "userId": user_id,
        "hospitalName": hospital_name or "",
        "address": address or "",
        "phone": phone,
        "icuCapacity": icu_capacity,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
    }
