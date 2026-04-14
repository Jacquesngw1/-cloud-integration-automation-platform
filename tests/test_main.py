"""Tests for the FastAPI application endpoints.

External HTTP calls and the database are both mocked so the test suite runs
without any network access or a running PostgreSQL instance.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=True)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


_SAMPLE_POSTS = [
    {"id": 1, "userId": 1, "title": "hello world", "body": "some body"},
    {"id": 2, "userId": 2, "title": "second post", "body": "another body"},
]


def _mock_httpx_client(json_data):
    """Return a mock httpx.AsyncClient whose get() returns *json_data*."""
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    return mock_client


@patch("app.main.httpx.AsyncClient")
def test_fetch_data(mock_async_client):
    mock_async_client.return_value = _mock_httpx_client(_SAMPLE_POSTS)

    response = client.get("/fetch-data")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 2
    assert data["data"][0]["external_id"] == 1
    assert data["data"][0]["title"] == "Hello World"


@patch("app.main.httpx.AsyncClient")
def test_store_data(mock_async_client):
    mock_async_client.return_value = _mock_httpx_client(_SAMPLE_POSTS)

    # Mock DB session: execute returns empty result (no existing IDs)
    mock_db = MagicMock()
    mock_db.execute.return_value = iter([])  # no pre-existing records
    mock_db.bulk_insert_mappings = MagicMock()
    mock_db.commit = MagicMock()

    def override_get_db():
        yield mock_db

    app.dependency_overrides[__import__("app.database", fromlist=["get_db"]).get_db] = override_get_db
    try:
        response = client.post("/store-data")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["stored"] == 2
    assert data["skipped"] == 0

