import logging
import re

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from database.connection import (
    get_donors_collection,
    get_hospitals_collection,
    get_notifications_collection,
    get_recipients_collection,
    get_users_collection,
)
from models.user import serialize_user, user_document
from schemas.auth import LoginRequest, SignupRequest, TokenResponse
from utils.jwt_handler import create_access_token
from utils.security import hash_password, verify_password

logger = logging.getLogger("livora.auth")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _find_user_by_email(users, email: str) -> dict | None:
    """Case-insensitive email lookup for new and legacy user documents."""
    normalized = _normalize_email(email)
    user = users.find_one({"email": normalized})
    if user:
        return user
    return users.find_one(
        {"email": {"$regex": f"^{re.escape(normalized)}$", "$options": "i"}}
    )


def _get_stored_password_hash(user: dict) -> str | None:
    for field in ("hashedPassword", "hashed_password", "password"):
        value = user.get(field)
        if isinstance(value, str) and value:
            return value
    return None


def ensure_indexes() -> None:
    users = get_users_collection()
    users.create_index("email", unique=True)
    get_donors_collection().create_index("userId", unique=True)
    get_recipients_collection().create_index("userId", unique=True)
    get_hospitals_collection().create_index("userId", unique=True)
    notifications = get_notifications_collection()
    notifications.create_index([("userId", 1), ("createdAt", -1)])
    notifications.create_index([("userId", 1), ("read", 1)])


def signup_user(payload: SignupRequest) -> TokenResponse:
    """Create user account and JWT only — no role profile documents."""
    users = get_users_collection()
    email = _normalize_email(payload.email)

    if _find_user_by_email(users, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    doc = user_document(
        full_name=payload.fullName,
        email=email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )

    logger.info("[MONGO] Writing to collection: users")
    try:
        result = users.insert_one(doc)
        logger.info("[MONGO] User inserted successfully: %s", result.inserted_id)
    except DuplicateKeyError as exc:
        logger.error("[MONGO] Insert failed: duplicate email %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        ) from exc
    except Exception as exc:
        logger.error("[MONGO] Insert failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        ) from exc

    user_id = str(result.inserted_id)
    token = create_access_token(subject=user_id, role=payload.role)
    return TokenResponse(
        access_token=token,
        userId=user_id,
        role=payload.role,
        fullName=payload.fullName,
    )


def login_user(payload: LoginRequest) -> TokenResponse:
    users = get_users_collection()
    email = _normalize_email(payload.email)
    logger.info("[LOGIN] Email received: %s", email)

    user = _find_user_by_email(users, email)
    logger.info("[LOGIN] User found: %s", user is not None)

    stored_hash = _get_stored_password_hash(user) if user else None
    password_ok = bool(
        user and stored_hash and verify_password(payload.password, stored_hash)
    )
    logger.info("[LOGIN] Password verification: %s", password_ok)

    if not user or not password_ok:
        if not user:
            logger.warning("[LOGIN] Login failed reason: user not found for email %s", email)
        elif not stored_hash:
            logger.warning(
                "[LOGIN] Login failed reason: missing password hash for user %s",
                user.get("_id"),
            )
        else:
            logger.warning("[LOGIN] Login failed reason: invalid password for %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_id = str(user["_id"])
    token = create_access_token(subject=user_id, role=user["role"])
    return TokenResponse(
        access_token=token,
        userId=user_id,
        role=user["role"],
        fullName=user["fullName"],
    )


def get_user_by_id(user_id: str) -> dict:
    try:
        oid = ObjectId(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user id",
        ) from exc

    user = get_users_collection().find_one({"_id": oid})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return serialize_user(user)
