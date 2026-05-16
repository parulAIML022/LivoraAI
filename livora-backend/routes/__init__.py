from routes.auth import router as auth_router
from routes.donors import router as donors_router
from routes.recipients import router as recipients_router

__all__ = ["auth_router", "donors_router", "recipients_router"]
