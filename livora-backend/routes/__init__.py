from routes.admin import router as admin_router
from routes.auth import router as auth_router
from routes.dashboard import router as dashboard_router
from routes.donors import router as donors_router
from routes.matching import router as matching_router
from routes.notifications import router as notifications_router
from routes.recipients import router as recipients_router

__all__ = [
    "auth_router",
    "donors_router",
    "recipients_router",
    "matching_router",
    "notifications_router",
    "dashboard_router",
    "admin_router",
]
