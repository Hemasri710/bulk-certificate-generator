import pytest
from fastapi import status


def test_create_job_invalid_email(client):
    """Test job creation fails with 422 when recipient email is invalid."""
    payload = {
        "event_name": "Python Summit 2026",
        "event_date": "2026-10-15",
        "recipients": [
            {"name": "Valid User", "email": "valid@example.com"},
            {"name": "Invalid User", "email": "not-an-email"},
        ],
    }
    response = client.post("/api/v1/jobs/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_create_job_empty_recipients(client):
    """Test job creation fails when recipient list is empty."""
    payload = {
        "event_name": "Python Summit 2026",
        "event_date": "2026-10-15",
        "recipients": [],
    }
    response = client.post("/api/v1/jobs/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_empty_event_name(client):
    """Test job creation fails when event name is empty or whitespace."""
    payload = {
        "event_name": "   ",
        "event_date": "2026-10-15",
        "recipients": [{"name": "Hemasri", "email": "hema@example.com"}],
    }
    response = client.post("/api/v1/jobs/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_job_blank_recipient_name(client):
    """Test job creation fails when recipient name is blank."""
    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-15",
        "recipients": [{"name": "  ", "email": "hema@example.com"}],
    }
    response = client.post("/api/v1/jobs/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
