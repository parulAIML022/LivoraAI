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

    if users.find_one({"email": payload.email.lower()}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    doc = user_document(
        full_name=payload.fullName,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )

    try:
        result = users.insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
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
    user = users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["hashedPassword"]):
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
