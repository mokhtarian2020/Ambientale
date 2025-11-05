from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    patients,
    diseases,
    environmental,
    investigations,
    analytics,
    dashboard,
    istat_analytics
)
from app.pipeline.data_pipeline import pipeline_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(diseases.router, prefix="/diseases", tags=["diseases"])
api_router.include_router(environmental.router, prefix="/environmental", tags=["environmental"])
api_router.include_router(investigations.router, prefix="/investigations", tags=["investigations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(istat_analytics.router, prefix="/", tags=["istat-analytics"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["data-pipeline"])
