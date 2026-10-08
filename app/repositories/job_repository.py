from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.job import GenerationJob, JobStatus


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, event_name: str, event_date: str, total_recipients: int) -> GenerationJob:
        job = GenerationJob(
            event_name=event_name,
            event_date=event_date,
            total_recipients=total_recipients,
            status=JobStatus.PENDING,
            successful_count=0,
            failed_count=0,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_id(self, job_id: str) -> Optional[GenerationJob]:
        return self.db.query(GenerationJob).filter(GenerationJob.id == job_id).first()

    def update_job_status(self, job_id: str, status: JobStatus) -> Optional[GenerationJob]:
        job = self.get_job_by_id(job_id)
        if job:
            job.status = status
            if status == JobStatus.PROCESSING and not job.started_at:
                job.started_at = datetime.now(timezone.utc)
            elif status in [JobStatus.COMPLETED, JobStatus.PARTIALLY_COMPLETED, JobStatus.FAILED]:
                job.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(job)
        return job

    def increment_counts(self, job_id: str, is_success: bool) -> Optional[GenerationJob]:
        job = self.get_job_by_id(job_id)
        if job:
            if is_success:
                job.successful_count += 1
            else:
                job.failed_count += 1
            self.db.commit()
            self.db.refresh(job)
        return job

    def get_all_jobs(self, limit: int = 50, offset: int = 0) -> List[GenerationJob]:
        return (
            self.db.query(GenerationJob)
            .order_by(GenerationJob.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
