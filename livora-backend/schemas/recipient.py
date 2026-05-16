from typing import Literal

from pydantic import BaseModel, Field

RecipientStatus = Literal["pending", "verified", "active", "inactive"]


class RecipientUpdateRequest(BaseModel):
    organNeeded: str | None = None
    organs: list[str] | None = None
    bloodGroup: str | None = None
    age: int | None = Field(None, ge=1, le=120)
    gender: str | None = None
    phone: str | None = None
    address: str | None = None
    medicalHistory: str | None = None
    status: RecipientStatus | None = None


class RecipientResponse(BaseModel):
    id: str
    userId: str
    organNeeded: str | None = None
    organs: list[str] = []
    bloodGroup: str | None = None
    age: int | None = None
    gender: str | None = None
    phone: str | None = None
    address: str | None = None
    medicalHistory: str | None = None
    status: str = "pending"
    profileCompletion: int = 0
    createdAt: str
    updatedAt: str
