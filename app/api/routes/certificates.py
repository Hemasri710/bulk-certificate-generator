from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ErrorResponse
from app.services.certificate_service import CertificateService

router = APIRouter(prefix="/certificates", tags=["Certificates"])


@router.get(
    "/{certificate_id}/download",
    summary="Download Certificate PDF",
    description="Retrieves and streams the generated certificate PDF file for a given certificate ID.",
    responses={
        200: {"content": {"application/pdf": {}}, "description": "PDF certificate file download"},
        400: {"model": ErrorResponse, "description": "Certificate is pending or generation failed"},
        404: {"model": ErrorResponse, "description": "Certificate record or file not found"},
    },
)
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    file_path, filename, error_code = CertificateService.get_certificate_download_path(
        certificate_id, db
    )

    if error_code == "CERTIFICATE_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate with ID '{certificate_id}' was not found.",
        )

    if error_code in ["CERTIFICATE_GENERATION_FAILED", "CERTIFICATE_STILL_PENDING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Certificate '{certificate_id}' is not available for download (Status detail: {error_code}).",
        )

    if error_code in ["FILE_NOT_FOUND_ON_STORAGE", "SECURITY_PATH_TRAVERSAL_REJECTED"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested certificate PDF file is unavailable or access was restricted.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
