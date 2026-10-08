import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"
    GENERATED = "GENERATED"
    FAILED = "FAILED"


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False, index=True)
    certificate_number = Column(String(100), unique=True, index=True, nullable=False)
    
    status = Column(Enum(CertificateStatus), nullable=False, default=CertificateStatus.PENDING, index=True)
    file_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    job = relationship("GenerationJob", back_populates="certificates")
