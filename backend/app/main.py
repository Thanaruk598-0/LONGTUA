from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="LONGTUA API",
    description="Personal Adaptive Planner",
    version="0.1.0",
)

app.include_router(health_router)
