from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": "Generation job with ID '123e4567-e89b-12d3-a456-426614174000' was not found.",
                }
            }
        }
    )
