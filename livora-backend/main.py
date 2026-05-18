import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import CORS_ORIGINS, UPLOAD_DIR
from database.connection import get_client
from routes import (
    admin_router,
    auth_router,
    dashboard_router,
    donors_router,
    matching_router,
    notifications_router,
    recipients_router,
)
from services.auth_service import ensure_indexes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("livora.matching").setLevel(logging.INFO)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    get_client().admin.command("ping")
    ensure_indexes()
    yield


app = FastAPI(
    title="Livora API",
    description="Organ donation platform — Phase 2: Dynamic dashboards & matching",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(donors_router)
app.include_router(recipients_router)
app.include_router(matching_router)
app.include_router(notifications_router)
app.include_router(dashboard_router)
app.include_router(admin_router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/", tags=["Health"])
def health():
    return {"message": "Livora API is running", "docs": "/docs"}
