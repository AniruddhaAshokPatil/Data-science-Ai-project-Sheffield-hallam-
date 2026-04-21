from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, WebSocket
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import get_websocket_user, hash_password
from src.api.config import settings
from src.api.db import init_database, upsert_user_with_email
from src.api.routers.auth import router as auth_router
from src.api.routers.health import router as health_router
from src.api.routers.insurance import router as insurance_router
from src.api.websocket_manager import alert_stream_manager


@asynccontextmanager
async def lifespan(_: FastAPI):
    # I initialise the runtime database and upload directory here so deployments boot into a ready state.
    init_database()
    settings.EVIDENCE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    _seed_default_users()
    yield


app = FastAPI(
    title="ShieldWise Insurance Fraud API",
    version="1.0.0",
    description="I provide the claims, dashboard, and live alert endpoints for the insurance fraud website.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(insurance_router)


@app.get("/")
def api_root() -> dict:
    # I expose a small root payload here so the API has a human-readable landing endpoint in the browser.
    return {
        "name": app.title,
        "version": app.version,
        "status": "ok",
        "docs_url": "/docs",
        "health_live_url": "/health/live",
        "health_ready_url": "/health/ready",
    }


@app.websocket("/ws/alerts")
async def claim_alerts_stream(websocket: WebSocket) -> None:
    # I keep the live alert stream separate from the REST endpoints because the dashboard needs push updates.
    try:
        authenticated_user = get_websocket_user(token=websocket.query_params.get("token"))
        if authenticated_user.role != "investigator":
            await websocket.close(code=4403)
            return
    except HTTPException:
        await websocket.close(code=4401)
        return

    await alert_stream_manager.stream_claim_alerts(websocket)


def _seed_default_users() -> None:
    # I seed default demo accounts here so the production-style auth flow works out of the box in local environments.
    user_salt, user_hash = hash_password(os.getenv("SHIELDWISE_DEFAULT_USER_PASSWORD", "UserPass123!"))
    upsert_user_with_email(
        username=os.getenv("SHIELDWISE_DEFAULT_USER_USERNAME", "demo_user"),
        full_name="Demo Policyholder",
        email=os.getenv("SHIELDWISE_DEFAULT_USER_EMAIL", "demo_user@shieldwise.local"),
        role="user",
        password_salt=user_salt,
        password_hash=user_hash,
    )

    investigator_salt, investigator_hash = hash_password(
        os.getenv("SHIELDWISE_DEFAULT_INVESTIGATOR_PASSWORD", "InvestigatorPass123!")
    )
    upsert_user_with_email(
        username=os.getenv("SHIELDWISE_DEFAULT_INVESTIGATOR_USERNAME", "investigator_anna"),
        full_name="Anna Hughes",
        email=os.getenv("SHIELDWISE_DEFAULT_INVESTIGATOR_EMAIL", "anna.hughes@shieldwise.local"),
        role="investigator",
        password_salt=investigator_salt,
        password_hash=investigator_hash,
    )
