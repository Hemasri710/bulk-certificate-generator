"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-08 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create generation_jobs table
    op.create_table(
        "generation_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_name", sa.String(length=255), nullable=False),
        sa.Column("event_date", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PROCESSING", "COMPLETED", "PARTIALLY_COMPLETED", "FAILED", name="jobstatus"),
            nullable=False,
        ),
        sa.Column("total_recipients", sa.Integer(), nullable=False),
        sa.Column("successful_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generation_jobs_event_name"), "generation_jobs", ["event_name"], unique=False)
    op.create_index(op.f("ix_generation_jobs_status"), "generation_jobs", ["status"], unique=False)

    # Create certificates table
    op.create_table(
        "certificates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("certificate_number", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "GENERATED", "FAILED", name="certificatestatus"),
            nullable=False,
        ),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["generation_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certificates_certificate_number"), "certificates", ["certificate_number"], unique=True)
    op.create_index(op.f("ix_certificates_job_id"), "certificates", ["job_id"], unique=False)
    op.create_index(op.f("ix_certificates_recipient_email"), "certificates", ["recipient_email"], unique=False)
    op.create_index(op.f("ix_certificates_status"), "certificates", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_certificates_status"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_recipient_email"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_job_id"), table_name="certificates")
    op.drop_index(op.f("ix_certificates_certificate_number"), table_name="certificates")
    op.drop_table("certificates")
    op.drop_index(op.f("ix_generation_jobs_status"), table_name="generation_jobs")
    op.drop_index(op.f("ix_generation_jobs_event_name"), table_name="generation_jobs")
    op.drop_table("generation_jobs")
