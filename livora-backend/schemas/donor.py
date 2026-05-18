from typing import Literal

from pydantic import BaseModel, Field

DonorStatus = Literal["pending", "verified", "active", "inactive"]

# Allowed values for hospital/admin status updates only
VALID_DONOR_STATUSES = frozenset({"pending", "verified", "active", "inactive"})


class DonorUpdateRequest(BaseModel):
    """Donor self-service fields — approval status is never accepted here."""

    bloodGroup: str | None = None
    organs: list[str] | None = None
    age: int | None = Field(None, ge=1, le=120)
    gender: str | None = None
    phone: str | None = None
    address: str | None = None
    medicalHistory: str | None = None


class DonorStatusUpdateRequest(BaseModel):
    """Hospital/admin only — updates donor approval status."""

    status: DonorStatus


class DocumentInfo(BaseModel):
    filename: str
    originalName: str
    contentType: str
    uploadedAt: str
    url: str


class DonorResponse(BaseModel):
    id: str
    userId: str
    bloodGroup: str | None = None
    organs: list[str] = []
    age: int | None = None
    gender: str | None = None
    phone: str | None = None
    address: str | None = None
    medicalHistory: str | None = None
    documents: list[DocumentInfo] = []
    status: str = "pending"
    profileCompletion: int = 0
    createdAt: str
    updatedAt: str
