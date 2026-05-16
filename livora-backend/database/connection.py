from pymongo import MongoClient
from pymongo.database import Database

from config import MONGODB_DB_NAME, MONGODB_URI

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URI)
    return _client


def get_database() -> Database:
    return get_client()[MONGODB_DB_NAME]


def get_users_collection():
    return get_database()["users"]


def get_donors_collection():
    return get_database()["donors"]


def get_recipients_collection():
    return get_database()["recipients"]


def get_hospitals_collection():
    return get_database()["hospitals"]
