from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.certificate import CertificateStatus


class CertificateResponse(BaseModel):
    id: str
    recipient_name: str
    recipient_email: str
    certificate_number: str
    status: CertificateStatus
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    generated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "e4e89b4f-8012-4217-bf4a-9b1686d17e5a",
                "recipient_name": "Hemasri",
                "recipient_email": "hema@example.com",
                "certificate_number": "CERT-2026-0001",
                "status": "GENERATED",
                "download_url": "/api/v1/certificates/e4e89b4f-8012-4217-bf4a-9b1686d17e5a/download",
                "error_message": None,
                "created_at": "2026-10-08T22:00:00Z",
                "generated_at": "2026-10-08T22:00:02Z",
            }
        },
    )


class CertificateListResponse(BaseModel):
    job_id: str
    total: int
    certificates: List[CertificateResponse]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "b3c79a95-3df1-4a87-8488-8254b7c6c401",
                "total": 1,
                "certificates": [
                    {
                        "id": "e4e89b4f-8012-4217-bf4a-9b1686d17e5a",
                        "recipient_name": "Hemasri",
                        "recipient_email": "hema@example.com",
                        "certificate_number": "CERT-2026-0001",
                        "status": "GENERATED",
                        "download_url": "/api/v1/certificates/e4e89b4f-8012-4217-bf4a-9b1686d17e5a/download",
                        "error_message": None,
                        "created_at": "2026-10-08T22:00:00Z",
                        "generated_at": "2026-10-08T22:00:02Z",
                    }
                ],
            }
        }
    )
