from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.certificate import Certificate, CertificateStatus


class CertificateRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create_certificates(self, certificates_data: List[dict]) -> List[Certificate]:
        certificates = [Certificate(**data) for data in certificates_data]
        self.db.add_all(certificates)
        self.db.commit()
        for cert in certificates:
            self.db.refresh(cert)
        return certificates

    def get_certificate_by_id(self, certificate_id: str) -> Optional[Certificate]:
        return self.db.query(Certificate).filter(Certificate.id == certificate_id).first()

    def get_certificates_by_job_id(
        self, job_id: str, limit: int = 100, offset: int = 0
    ) -> List[Certificate]:
        return (
            self.db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .order_by(Certificate.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def mark_generated(self, certificate_id: str, file_path: str) -> Optional[Certificate]:
        cert = self.get_certificate_by_id(certificate_id)
        if cert:
            cert.status = CertificateStatus.GENERATED
            cert.file_path = file_path
            cert.generated_at = datetime.now(timezone.utc)
            cert.error_message = None
            self.db.commit()
            self.db.refresh(cert)
        return cert

    def mark_failed(self, certificate_id: str, error_message: str) -> Optional[Certificate]:
        cert = self.get_certificate_by_id(certificate_id)
        if cert:
            cert.status = CertificateStatus.FAILED
            cert.error_message = error_message
            self.db.commit()
            self.db.refresh(cert)
        return cert
