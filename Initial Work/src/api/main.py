import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.api.config import cfg
from src.api.logger import logger
from src.api.routers.analytics import router as analytics_router
from src.api.routers.cv import router as cv_router
from src.api.routers.nlp import router as nlp_router
from src.api.routers.transactions import score_transaction_features
from src.api.routers.transactions import router as transactions_router
from src.api.services.rate_limit import InMemoryRateLimiter
from src.api.services.readiness import get_readiness_report
from src.api.websocket_manager import WebSocketManager


# I create one shared WebSocket manager so I can track all live dashboard
# clients in one place instead of managing connections inside the route itself.
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # I log startup and shutdown here because production services are easier
    # to operate when I can see exactly when the API came online.
    logger.info("Starting Fraud Detection API in %s mode.", cfg.app_env)
    yield
    logger.info("Stopping Fraud Detection API.")


def create_app() -> FastAPI:
    # I build the app through a factory because that makes testing and future
    # deployment wiring much easier than relying on module side effects alone.
    app = FastAPI(
        title="Fraud Detection API",
        version=cfg.app_version,
        description="Unified API for transaction, NLP, analytics, and CV fraud scoring.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=cfg.trusted_hosts)
    limiter = InMemoryRateLimiter(
        max_requests=cfg.rate_limit_requests,
        window_seconds=cfg.rate_limit_window_seconds,
    )

    # I include separate routers so each fraud area can stay in its own file
    # while still becoming part of one complete backend application.
    app.include_router(transactions_router)
    app.include_router(nlp_router)
    app.include_router(analytics_router)
    app.include_router(cv_router)

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        # I expose request duration in a header because it helps me observe API
        # latency without changing every single route implementation.
        from time import perf_counter

        client_host = request.client.host if request.client else "unknown"
        allowed, retry_after = limiter.check(client_host)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests."},
                headers={"Retry-After": str(retry_after)},
            )

        started_at = perf_counter()
        response = await call_next(request)
        duration = perf_counter() - started_at
        response.headers["X-Process-Time"] = f"{duration:.6f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "connect-src 'self' ws: wss: http: https:; "
            "script-src 'self';"
        )
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # I keep one fallback error handler so unexpected failures are logged
        # consistently and clients receive a stable JSON response shape.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    @app.get("/")
    def root():
        # I keep this route simple because I use it as a quick confirmation that
        # the backend is alive and to remind myself which main routes exist.
        response = {
            "message": "Fraud Detection API is running.",
            "environment": cfg.app_env,
            "version": cfg.app_version,
            "routes": [
                "/transaction/predict",
                "/nlp/predict",
                "/analytics/visualize",
                "/analytics/outliers",
                "/cv/predict",
            ],
        }
        return response

    @app.get("/health")
    def health():
        # I use a health route because tools, tests, and deployment checks often
        # need a tiny endpoint that proves the server is responding.
        response = {
            "status": "ok",
            "environment": cfg.app_env,
            "version": cfg.app_version,
        }
        return response

    @app.get("/health/live")
    def live_health():
        # I keep liveness minimal because orchestration tools usually only need
        # to know whether the process can answer requests at all.
        return {"status": "ok"}

    @app.get("/health/ready")
    def readiness_health():
        # I expose a structured readiness view here because production systems
        # need to see which models and assets are available before routing traffic.
        report = get_readiness_report()
        status_code = 200 if report["ready"] else 503
        return JSONResponse(status_code=status_code, content=report)

    @app.websocket("/ws/transactions")
    async def transactions_websocket(websocket: WebSocket):
        # I use a WebSocket here because the dashboard can listen for live
        # transaction updates without repeatedly sending normal HTTP requests.
        await ws_manager.connect(websocket)
        try:
            while True:
                raw_message = await websocket.receive_text()
                if raw_message.strip().lower() == "ping":
                    pong_message = {"type": "pong"}
                    await websocket.send_json(pong_message)
                    continue

                payload = json.loads(raw_message)
                features = payload.get("features")
                if not isinstance(features, dict):
                    error_message = {"error": "Payload must include a features object."}
                    await websocket.send_json(error_message)
                    continue

                # I reuse the same transaction scoring function that the HTTP route
                # uses so the project has one shared source of scoring logic.
                result = score_transaction_features(features).model_dump()
                await ws_manager.broadcast(result)
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
        except json.JSONDecodeError:
            await websocket.send_json({"error": "Payload must be valid JSON."})
            ws_manager.disconnect(websocket)
        except Exception:
            ws_manager.disconnect(websocket)
            raise

    return app


app = create_app()
