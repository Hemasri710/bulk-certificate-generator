from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from app.models.job import JobStatus


class JobRecipient(BaseModel):
    name: str = Field(..., description="Recipient full name", min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Recipient valid email address")

    @field_validator("name")

    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Recipient name cannot be empty or blank")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Hemasri",
                "email": "hema@example.com",
            }
        }
    )


class JobCreate(BaseModel):
    event_name: str = Field(..., description="Event or Workshop Name", min_length=1, max_length=255)
    event_date: str = Field(..., description="Event Date (e.g. 2026-10-15)", min_length=4)
    recipients: List[JobRecipient] = Field(..., description="List of recipients to receive certificates", min_length=1)

    @field_validator("event_name")
    @classmethod
    def event_name_must_not_be_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Event name cannot be empty or blank")
        return cleaned

    @field_validator("event_date")
    @classmethod
    def event_date_must_not_be_blank(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Event date cannot be empty or blank")
        return cleaned

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_name": "Python Backend Workshop 2026",
                "event_date": "2026-10-15",
                "recipients": [
                    {"name": "Hemasri", "email": "hema@example.com"},
                    {"name": "Ananya", "email": "ananya@example.com"},
                ],
            }
        }
    )


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus
    total_recipients: int
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "b3c79a95-3df1-4a87-8488-8254b7c6c401",
                "status": "PENDING",
                "total_recipients": 2,
                "message": "Certificate generation job created successfully",
            }
        }
    )


class JobStatusResponse(BaseModel):
    job_id: str
    event_name: str
    event_date: str
    status: JobStatus
    total_recipients: int
    successful_count: int
    failed_count: int
    pending_count: int
    progress_percentage: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "job_id": "b3c79a95-3df1-4a87-8488-8254b7c6c401",
                "event_name": "Python Backend Workshop 2026",
                "event_date": "2026-10-15",
                "status": "PROCESSING",
                "total_recipients": 10,
                "successful_count": 6,
                "failed_count": 1,
                "pending_count": 3,
                "progress_percentage": 70.0,
                "created_at": "2026-10-08T22:00:00Z",
                "started_at": "2026-10-08T22:00:01Z",
                "completed_at": None,
            }
        },
    )
