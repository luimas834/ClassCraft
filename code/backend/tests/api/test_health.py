"""Tests for the health endpoint."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.main import app

client = TestClient(app)


def test_health_says_ok_when_the_database_answers() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok", "version": "0.1.0"}


def test_health_says_503_when_the_database_is_down() -> None:
    failure = OperationalError("SELECT 1", {}, Exception("no connection"))

    with patch("app.routers.health.engine.connect", side_effect=failure):
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json()["db"] == "down"
