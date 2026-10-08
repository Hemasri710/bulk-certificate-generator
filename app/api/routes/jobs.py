from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.schemas.job import JobCreate, JobCreateResponse, JobStatusResponse
from app.schemas.certificate import CertificateListResponse
from app.schemas.common import ErrorResponse
from app.services.job_service import JobService
from app.services.certificate_service import CertificateService
from app.repositories.job_repository import JobRepository

router = APIRouter(prefix="/jobs", tags=["Generation Jobs"])


@router.post(
    "/",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Bulk Certificate Generation Job",
    description="Creates a new bulk certificate generation job and starts PDF generation asynchronously in background tasks.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data or recipient list"},
        422: {"model": ErrorResponse, "description": "Unprocessable validation entity"},
    },
)
def create_generation_job(
    job_in: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if len(job_in.recipients) > settings.MAX_RECIPIENTS_PER_JOB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipient count exceeds maximum allowed limit of {settings.MAX_RECIPIENTS_PER_JOB}.",
        )

    # 1. Create job and initial certificate records in database
    job_response = JobService.create_bulk_job(job_in, db)

    # 2. Schedule background processing without blocking client
    background_tasks.add_task(JobService.process_job_background, job_response.job_id)

    return job_response


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Get Job Progress and Status",
    description="Returns current status, progress percentage, total recipient counts, and timestamps for a specific job.",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    status_response = JobService.get_job_status(job_id, db)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID '{job_id}' was not found.",
        )
    return status_response


@router.get(
    "/{job_id}/certificates",
    response_model=CertificateListResponse,
    summary="Get Certificates for Job",
    description="Returns all certificate records associated with a specific generation job.",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    },
)
def get_job_certificates(
    job_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    cert_list = CertificateService.get_job_certificates(job_id, db, limit=limit, offset=offset)
    if cert_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Generation job with ID '{job_id}' was not found.",
        )
    return cert_list


@router.get(
    "/",
    summary="List Recent Jobs",
    description="Returns list of recent generation jobs for administration overview.",
)
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    repo = JobRepository(db)
    jobs = repo.get_all_jobs(limit=limit, offset=offset)
    
    results = []
    for job in jobs:
        status_resp = JobService.get_job_status(job.id, db)
        if status_resp:
            results.append(status_resp)
    return {"jobs": results}
