from unittest.mock import patch
from fastapi import status
from app.services.pdf_service import PDFCertificateGenerator


def test_partial_failure_handling(client):
    """Test that failure on 1 recipient does not halt processing of other recipients.

    Job should complete with PARTIALLY_COMPLETED status.
    """
    payload = {
        "event_name": "Resilience Engineering Seminar",
        "event_date": "2026-11-10",
        "recipients": [
            {"name": "Good Recipient 1", "email": "good1@example.com"},
            {"name": "Bad Recipient", "email": "bad@example.com"},
            {"name": "Good Recipient 2", "email": "good2@example.com"},
        ],
    }

    original_generate = PDFCertificateGenerator.generate_certificate

    def mock_generate(recipient_name, *args, **kwargs):
        if recipient_name == "Bad Recipient":
            raise RuntimeError("Simulated PDF Rendering Crash")
        return original_generate(recipient_name, *args, **kwargs)

    # Wrap POST in patch context so background task executes with mock active
    with patch.object(PDFCertificateGenerator, "generate_certificate", side_effect=mock_generate):
        create_res = client.post("/api/v1/jobs/", json=payload)

    assert create_res.status_code == status.HTTP_201_CREATED
    job_id = create_res.json()["job_id"]

    # Check job status
    status_res = client.get(f"/api/v1/jobs/{job_id}")
    assert status_res.status_code == status.HTTP_200_OK
    status_data = status_res.json()

    assert status_data["status"] == "PARTIALLY_COMPLETED"
    assert status_data["total_recipients"] == 3
    assert status_data["successful_count"] == 2
    assert status_data["failed_count"] == 1
    assert status_data["pending_count"] == 0

    # Verify certificate list reflects individual statuses
    cert_res = client.get(f"/api/v1/jobs/{job_id}/certificates")
    certs = cert_res.json()["certificates"]

    bad_cert = next(c for c in certs if c["recipient_name"] == "Bad Recipient")
    assert bad_cert["status"] == "FAILED"
    assert "Simulated PDF Rendering Crash" in bad_cert["error_message"]

    good_certs = [c for c in certs if c["recipient_name"] != "Bad Recipient"]
    assert len(good_certs) == 2
    assert all(c["status"] == "GENERATED" for c in good_certs)
