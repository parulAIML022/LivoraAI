import logging

from pymongo import MongoClient
from pymongo.database import Database

from config import MONGODB_DB_NAME, MONGODB_URI

logger = logging.getLogger("livora.mongo")

_client: MongoClient | None = None
_db_verified = False


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        _verify_connection()
    return _client


def _verify_connection() -> None:
    global _db_verified
    if _db_verified or _client is None:
        return
    try:
        _client.admin.command("ping")
        host = "unknown"
        if MONGODB_URI.startswith("mongodb://localhost") or MONGODB_URI.startswith("mongodb://127.0.0.1"):
            host = "localhost"
        elif "@" in MONGODB_URI:
            host = MONGODB_URI.split("@", 1)[1].split("/")[0].split("?")[0]
        logger.info(
            "[MONGO] Connected to database: %s (host: %s)",
            MONGODB_DB_NAME,
            host,
        )
        _db_verified = True
    except Exception as exc:
        logger.error("[MONGO] Connection failed: %s", exc)
        raise


def get_database() -> Database:
    _verify_connection()
    return get_client()[MONGODB_DB_NAME]


def get_users_collection():
    return get_database()["users"]


def get_donors_collection():
    return get_database()["donors"]


def get_recipients_collection():
    return get_database()["recipients"]


def get_hospitals_collection():
    return get_database()["hospitals"]


def get_notifications_collection():
    return get_database()["notifications"]
