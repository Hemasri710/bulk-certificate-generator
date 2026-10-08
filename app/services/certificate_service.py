import os
from pathlib import Path
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.certificate import CertificateStatus
from app.repositories.certificate_repository import CertificateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.certificate import CertificateListResponse, CertificateResponse
from app.utils.file_utils import is_safe_path
from app.utils.validators import sanitize_filename


class CertificateService:
    """Service handling certificate listing and secure download file retrieval."""

    @staticmethod
    def get_job_certificates(
        job_id: str, db: Session, limit: int = 100, offset: int = 0
    ) -> Optional[CertificateListResponse]:
        job_repo = JobRepository(db)
        cert_repo = CertificateRepository(db)

        job = job_repo.get_job_by_id(job_id)
        if not job:
            return None

        certificates = cert_repo.get_certificates_by_job_id(job_id, limit=limit, offset=offset)

        cert_responses = []
        for c in certificates:
            download_url = f"{settings.API_V1_STR}/certificates/{c.id}/download" if c.status == CertificateStatus.GENERATED else None
            cert_responses.append(
                CertificateResponse(
                    id=c.id,
                    recipient_name=c.recipient_name,
                    recipient_email=c.recipient_email,
                    certificate_number=c.certificate_number,
                    status=c.status,
                    download_url=download_url,
                    error_message=c.error_message,
                    created_at=c.created_at,
                    generated_at=c.generated_at,
                )
            )

        return CertificateListResponse(
            job_id=job_id,
            total=len(cert_responses),
            certificates=cert_responses,
        )

    @staticmethod
    def get_certificate_download_path(
        certificate_id: str, db: Session
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Retrieves and validates the file path for a requested certificate download.

        Returns a tuple of: (file_path, suggested_filename, error_code)
        """
        cert_repo = CertificateRepository(db)
        cert = cert_repo.get_certificate_by_id(certificate_id)

        if not cert:
            return None, None, "CERTIFICATE_NOT_FOUND"

        if cert.status == CertificateStatus.FAILED:
            return None, None, "CERTIFICATE_GENERATION_FAILED"

        if cert.status == CertificateStatus.PENDING:
            return None, None, "CERTIFICATE_STILL_PENDING"

        if not cert.file_path or not os.path.exists(cert.file_path):
            return None, None, "FILE_NOT_FOUND_ON_STORAGE"

        # Security Check: Prevent Path Traversal Attacks
        if not is_safe_path(settings.STORAGE_DIR, cert.file_path):
            return None, None, "SECURITY_PATH_TRAVERSAL_REJECTED"

        safe_name = sanitize_filename(cert.recipient_name)
        download_filename = f"Certificate_{safe_name}_{cert.certificate_number}.pdf"

        return cert.file_path, download_filename, None
