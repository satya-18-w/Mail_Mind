"""Integration tests for FastAPI email routes."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.api.dependencies import get_current_user


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health_check():
    """Test the health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.anyio
async def test_list_emails_empty():
    """Test listing emails when database is empty."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_all_emails = AsyncMock(return_value=[])
            response = await client.get("/api/v1/emails")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_email_not_found():
    """Test getting a non-existent email."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_email_by_id = AsyncMock(return_value=None)
            response = await client.get("/api/v1/emails/999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_invalid_category():
    """Test requesting an invalid category."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emails/category/InvalidCat")
    assert response.status_code == 400


@pytest.mark.anyio
async def test_invalid_priority():
    """Test requesting an invalid priority."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/emails/priority/URGENT")
    assert response.status_code == 400


@pytest.mark.anyio
async def test_valid_category():
    """Test requesting a valid category."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_emails_by_category = AsyncMock(return_value=[])
            response = await client.get("/api/v1/emails/category/Institute")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_valid_priority():
    """Test requesting a valid priority."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_emails_by_priority = AsyncMock(return_value=[])
            response = await client.get("/api/v1/emails/priority/HIGH")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_deadlines_endpoint():
    """Test deadlines endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_emails_with_deadlines = AsyncMock(return_value=[])
            response = await client.get("/api/v1/emails/deadlines/upcoming")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_category_stats():
    """Test category stats endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.get_category_counts = AsyncMock(return_value=[
                {"name": "Institute", "count": 5},
                {"name": "LinkedIn", "count": 20},
            ])
            response = await client.get("/api/v1/stats/categories")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_trigger_pipeline():
    """Test pipeline trigger endpoint returns started status."""
    transport = ASGITransport(app=app)
    async def fake_current_user():
        return MagicMock(id=1, gmail_access_token="token", gmail_refresh_token="refresh")

    app.dependency_overrides[get_current_user] = fake_current_user
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("backend.api.email_routes._run_pipeline"), patch("backend.api.email_routes.crud") as mock_crud:
            mock_crud.create_pipeline_run = AsyncMock(return_value=MagicMock(id=123))
            response = await client.post("/api/v1/pipeline/run")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
