from fastapi import status


def test_create_job_success(client):
    """Test successful job creation returns 201 Created and pending/processing job response."""
    payload = {
        "event_name": "AEREO AI Bootcamp 2026",
        "event_date": "2026-10-20",
        "recipients": [
            {"name": "Hemasri", "email": "hema@example.com"},
            {"name": "Ananya", "email": "ananya@example.com"},
        ],
    }
    response = client.post("/api/v1/jobs/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total_recipients"] == 2


def test_job_status_progress(client):
    """Test retrieving job status and progress percentage."""
    payload = {
        "event_name": "Backend Engineering Masterclass",
        "event_date": "2026-10-25",
        "recipients": [
            {"name": "Rahul Verma", "email": "rahul@example.com"},
            {"name": "Priya Sharma", "email": "priya@example.com"},
        ],
    }
    # TestClient automatically executes BackgroundTasks upon request completion
    post_res = client.post("/api/v1/jobs/", json=payload)
    assert post_res.status_code == status.HTTP_201_CREATED
    job_id = post_res.json()["job_id"]

    # Check status endpoint
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == status.HTTP_200_OK
    status_data = status_res.json()

    assert status_data["job_id"] == job_id
    assert status_data["status"] == "COMPLETED"
    assert status_data["total_recipients"] == 2
    assert status_data["successful_count"] == 2
    assert status_data["failed_count"] == 0
    assert status_data["pending_count"] == 0
    assert status_data["progress_percentage"] == 100.0


def test_get_non_existent_job_status(client):
    """Test fetching status for non-existent job ID returns 404."""
    response = client.get("/api/v1/jobs/non-existent-uuid-12345")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
