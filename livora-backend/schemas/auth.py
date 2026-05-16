from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from config import ROLE_ALIASES, VALID_ROLES

RoleType = Literal["donor", "recipient", "hospital", "admin"]


def normalize_role(role: str) -> str:
    role = role.strip().lower()
    role = ROLE_ALIASES.get(role, role)
    if role not in VALID_ROLES:
        raise ValueError(
            f"Invalid role. Must be one of: {', '.join(sorted(VALID_ROLES))}"
        )
    return role


class SignupRequest(BaseModel):
    """Authentication only — no medical or role-profile fields."""

    fullName: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return normalize_role(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    userId: str
    role: str
    fullName: str


class UserResponse(BaseModel):
    userId: str
    fullName: str
    email: str
    role: str
    createdAt: str
