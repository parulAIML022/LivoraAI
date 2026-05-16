import uuid
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from fastapi import HTTPException, UploadFile, status

from config import ALLOWED_UPLOAD_EXTENSIONS, MAX_UPLOAD_SIZE_MB, UPLOAD_DIR
from database.connection import get_donors_collection, get_users_collection
from models.donor import donor_document, serialize_donor
from schemas.donor import DonorUpdateRequest


def _ensure_donor_profile(user_id: str) -> dict:
    donors = get_donors_collection()
    donor = donors.find_one({"userId": user_id})
    if donor:
        return donor

    user = get_users_collection().find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "donor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a donor",
        )
    donors.insert_one(donor_document(user_id=user_id))
    donor = donors.find_one({"userId": user_id})
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create donor profile",
        )
    return donor


def get_donor_profile(user_id: str, base_url: str = "") -> dict:
    return serialize_donor(_ensure_donor_profile(user_id), base_url=base_url)


def update_donor_profile(user_id: str, payload: DonorUpdateRequest, base_url: str = "") -> dict:
    donors = get_donors_collection()
    _ensure_donor_profile(user_id)
    donor = donors.find_one({"userId": user_id})

    update_data = payload.model_dump(exclude_unset=True)
    if "organs" in update_data and update_data["organs"]:
        update_data["organs"] = [o.strip().lower() for o in update_data["organs"] if o.strip()]

    if not update_data:
        return serialize_donor(donor, base_url=base_url)

    update_data["updatedAt"] = datetime.now(timezone.utc)
    donors.update_one({"userId": user_id}, {"$set": update_data})
    return serialize_donor(_ensure_donor_profile(user_id), base_url=base_url)


def upload_donor_document(user_id: str, file: UploadFile, base_url: str = "") -> dict:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided",
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allowed file types: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}",
        )

    content = file.file.read()
    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds {MAX_UPLOAD_SIZE_MB}MB limit",
        )

    user_dir = UPLOAD_DIR / user_id
    user_dir.mkdir(parents=True, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = user_dir / stored_name
    file_path.write_bytes(content)

    now = datetime.now(timezone.utc).isoformat()
    doc_entry = {
        "filename": stored_name,
        "originalName": file.filename,
        "contentType": file.content_type or "application/octet-stream",
        "uploadedAt": now,
        "url": f"/uploads/{user_id}/{stored_name}",
    }

    donors = get_donors_collection()
    donor = donors.find_one({"userId": user_id})
    if not donor:
        donors.insert_one(donor_document(user_id=user_id))
    donors.update_one(
        {"userId": user_id},
        {
            "$push": {"documents": doc_entry},
            "$set": {"updatedAt": datetime.now(timezone.utc)},
        },
    )
    return get_donor_profile(user_id, base_url=base_url)
