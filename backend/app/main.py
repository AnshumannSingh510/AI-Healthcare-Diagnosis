from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Clinical decision-support prototype for chest X-ray analysis. "
        "NOT an approved medical device. All predictions require professional confirmation."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Serve stored images/heatmaps/reports for local dev (in production, front by nginx or S3+CDN)
app.mount("/storage", StaticFiles(directory="/app/storage"), name="storage")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}
