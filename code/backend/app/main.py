"""Creates the FastAPI application.
Mounts every router under /api/v1; the error handlers arrive in a later iteration.
"""

from fastapi import FastAPI

from app.config import settings
from app.routers import health

API_PREFIX = "/api/v1"

app = FastAPI(
    title="ClassCraft API",
    version=settings.app_version,
    description="The class routine generator for one department and one semester.",
)

app.include_router(health.router, prefix=API_PREFIX)
