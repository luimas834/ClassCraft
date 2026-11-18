"""The health endpoint.
Says whether the API is running and whether the database answers.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def read_health() -> JSONResponse:
    """Answer 200 while the database replies, and 503 while it does not."""
    body = {"status": "ok", "db": "ok", "version": settings.app_version}
    status_code = 200

    try:
        # The cheapest question a database can be asked.
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        body = {"status": "error", "db": "down", "version": settings.app_version}
        status_code = 503

    return JSONResponse(content=body, status_code=status_code)
