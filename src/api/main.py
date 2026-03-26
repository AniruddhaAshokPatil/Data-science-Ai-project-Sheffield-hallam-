from fastapi import FastAPI

from src.api.routers.analytics import router as analytics_router
from src.api.routers.cv import router as cv_router
from src.api.routers.nlp import router as nlp_router
from src.api.routers.transactions import router as transactions_router


app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    description="Unified API for transaction, NLP, analytics, and CV fraud scoring.",
)


@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running.",
        "routes": [
            "/transaction/predict",
            "/nlp/predict",
            "/analytics/visualize",
            "/analytics/outliers",
            "/cv/predict",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(transactions_router)
app.include_router(nlp_router)
app.include_router(analytics_router)
app.include_router(cv_router)
