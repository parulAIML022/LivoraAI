import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "livora")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

_cors_raw = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:8080,http://127.0.0.1:8080",
)
CORS_ORIGINS = [origin.strip() for origin in _cors_raw.split(",") if origin.strip()]

UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

VALID_ROLES = {"donor", "recipient", "hospital", "admin"}

# Frontend uses "coordinator" — map to admin without duplicating routes
ROLE_ALIASES = {"coordinator": "admin"}
