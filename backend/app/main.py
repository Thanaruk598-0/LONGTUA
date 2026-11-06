from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.planning import router as planning_router

app = FastAPI(
    title="LONGTUA API",
    description="Personal Adaptive Planner",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(planning_router)
