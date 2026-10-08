from fastapi import status


def test_list_and_download_certificates(client):
    """Test listing certificates for a completed job and downloading a PDF file."""
    payload = {
        "event_name": "Cloud Native Summit",
        "event_date": "2026-11-01",
        "recipients": [
            {"name": "Sneha Reddy", "email": "sneha@example.com"}
        ],
    }
    create_res = client.post("/api/v1/jobs/", json=payload)
    assert create_res.status_code == status.HTTP_201_CREATED
    job_id = create_res.json()["job_id"]

    # 1. Fetch certificate list for job
    list_res = client.get(f"/api/v1/jobs/{job_id}/certificates")
    assert list_res.status_code == status.HTTP_200_OK
    list_data = list_res.json()
    assert list_data["total"] == 1
    cert = list_data["certificates"][0]
    assert cert["status"] == "GENERATED"
    assert cert["recipient_name"] == "Sneha Reddy"
    assert cert["download_url"] is not None

    # 2. Download certificate PDF
    cert_id = cert["id"]
    download_res = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert download_res.status_code == status.HTTP_200_OK
    assert download_res.headers["content-type"] == "application/pdf"
    assert len(download_res.content) > 0  # Verify non-empty PDF binary bytes


def test_download_non_existent_certificate(client):
    """Test downloading non-existent certificate returns 404 Not Found."""
    response = client.get("/api/v1/certificates/invalid-cert-id/download")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "NOT_FOUND"
