import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.job import GenerationJob, JobStatus
from app.models.certificate import Certificate, CertificateStatus
from app.repositories.job_repository import JobRepository
from app.repositories.certificate_repository import CertificateRepository
from app.schemas.job import JobCreate, JobCreateResponse, JobStatusResponse
from app.services.pdf_service import PDFCertificateGenerator
from app.utils.validators import sanitize_filename, validate_email_address

logger = logging.getLogger("app.services.job_service")


class JobService:
    """Service handling bulk certificate generation job lifecycle and background orchestration."""

    @staticmethod
    def create_bulk_job(job_in: JobCreate, db: Session) -> JobCreateResponse:
        job_repo = JobRepository(db)
        cert_repo = CertificateRepository(db)

        # 1. Create Job record
        job = job_repo.create_job(
            event_name=job_in.event_name,
            event_date=job_in.event_date,
            total_recipients=len(job_in.recipients),
        )

        # 2. Create Certificate records in PENDING status
        cert_records = []
        for idx, recipient in enumerate(job_in.recipients, start=1):
            cert_uuid = str(uuid.uuid4())
            # Format clean, unique certificate number: CERT-<JOB_PREFIX>-<IDX>
            cert_num = f"CERT-{job.id[:8].upper()}-{idx:04d}"
            
            cert_records.append(
                {
                    "id": cert_uuid,
                    "job_id": job.id,
                    "recipient_name": recipient.name,
                    "recipient_email": recipient.email,
                    "certificate_number": cert_num,
                    "status": CertificateStatus.PENDING,
                }
            )

        cert_repo.bulk_create_certificates(cert_records)

        logger.info(f"Created bulk job '{job.id}' with {len(cert_records)} recipient certificates.")

        return JobCreateResponse(
            job_id=job.id,
            status=job.status,
            total_recipients=job.total_recipients,
            message="Certificate generation job created successfully",
        )

    @staticmethod
    def process_job_background(job_id: str) -> None:
        """Background worker function called by FastAPI BackgroundTasks.

        Uses its own dedicated database session to ensure isolation.
        """
        logger.info(f"[Background Worker] Starting processing for job_id: {job_id}")
        db = SessionLocal()

        try:
            job_repo = JobRepository(db)
            cert_repo = CertificateRepository(db)

            job = job_repo.get_job_by_id(job_id)
            if not job:
                logger.error(f"[Background Worker] Job '{job_id}' not found.")
                return

            # Mark job as PROCESSING
            job_repo.update_job_status(job_id, JobStatus.PROCESSING)

            certificates = cert_repo.get_certificates_by_job_id(job_id, limit=10000)
            pending_certs = [c for c in certificates if c.status == CertificateStatus.PENDING]

            for cert in pending_certs:
                # Process each recipient independently to ensure failure isolation
                try:
                    # Sanitize recipient name for filename
                    safe_name = sanitize_filename(cert.recipient_name)
                    relative_path = f"{job_id}/{cert.id}_{safe_name}.pdf"
                    full_file_path = settings.STORAGE_DIR / relative_path

                    # Generate PDF using ReportLab
                    PDFCertificateGenerator.generate_certificate(
                        recipient_name=cert.recipient_name,
                        event_name=job.event_name,
                        event_date=job.event_date,
                        certificate_number=cert.certificate_number,
                        output_file_path=str(full_file_path),
                    )

                    # Update certificate status
                    cert_repo.mark_generated(cert.id, str(full_file_path))
                    job_repo.increment_counts(job_id, is_success=True)
                    logger.info(f"Successfully generated certificate '{cert.id}' for {cert.recipient_email}")

                except Exception as e:
                    error_msg = f"PDF Generation failed: {str(e)}"
                    logger.error(f"Error generating certificate '{cert.id}' for {cert.recipient_email}: {error_msg}")
                    cert_repo.mark_failed(cert.id, error_msg)
                    job_repo.increment_counts(job_id, is_success=False)

            # Determine final job status
            refreshed_job = job_repo.get_job_by_id(job_id)
            if refreshed_job:
                if refreshed_job.successful_count == refreshed_job.total_recipients:
                    final_status = JobStatus.COMPLETED
                elif refreshed_job.successful_count > 0:
                    final_status = JobStatus.PARTIALLY_COMPLETED
                else:
                    final_status = JobStatus.FAILED

                job_repo.update_job_status(job_id, final_status)
                logger.info(
                    f"[Background Worker] Job '{job_id}' finished with status: {final_status}. "
                    f"Success: {refreshed_job.successful_count}, Failed: {refreshed_job.failed_count}"
                )

        except Exception as ex:
            logger.critical(f"[Background Worker] Unexpected error in job '{job_id}': {str(ex)}")
        finally:
            db.close()

    @staticmethod
    def get_job_status(job_id: str, db: Session) -> Optional[JobStatusResponse]:
        job_repo = JobRepository(db)
        job = job_repo.get_job_by_id(job_id)
        if not job:
            return None

        processed_count = job.successful_count + job.failed_count
        pending_count = max(0, job.total_recipients - processed_count)

        if job.total_recipients == 0:
            progress_pct = 100.0
        else:
            progress_pct = round((processed_count / job.total_recipients) * 100, 2)

        return JobStatusResponse(
            job_id=job.id,
            event_name=job.event_name,
            event_date=job.event_date,
            status=job.status,
            total_recipients=job.total_recipients,
            successful_count=job.successful_count,
            failed_count=job.failed_count,
            pending_count=pending_count,
            progress_percentage=progress_pct,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )
