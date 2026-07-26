"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = postgresql.ENUM("patient", "doctor", "admin", name="user_role")
    xray_status = postgresql.ENUM("uploaded", "processing", "completed", "failed", name="xray_status")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "patients",
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("gender", sa.String(32), nullable=True),
        sa.Column("medical_history", sa.Text, nullable=True),
        sa.Column("assigned_doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_patients_assigned_doctor_id", "patients", ["assigned_doctor_id"])

    op.create_table(
        "doctors",
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("specialization", sa.String(255), nullable=True),
        sa.Column("license_number", sa.String(128), nullable=True),
    )

    op.create_table(
        "xrays",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("image_path", sa.String(512), nullable=False),
        sa.Column("upload_time", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", xray_status, nullable=False),
    )
    op.create_index("ix_xrays_patient_id", "xrays", ["patient_id"])

    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("xray_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("xrays.id"), nullable=False),
        sa.Column("disease", sa.String(255), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("all_scores", sa.JSON, nullable=True),
        sa.Column("heatmap_path", sa.String(512), nullable=True),
        sa.Column("severity", sa.String(32), nullable=True),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("ai_explanation", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_predictions_xray_id", "predictions", ["xray_id"])

    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("prediction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("predictions.id"), nullable=False),
        sa.Column("doctor_comment", sa.Text, nullable=True),
        sa.Column("doctor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("pdf_path", sa.String(512), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_reports_prediction_id", "reports", ["prediction_id"])

    op.create_table(
        "chat_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_chat_history_user_id", "chat_history", ["user_id"])


def downgrade() -> None:
    op.drop_table("chat_history")
    op.drop_table("reports")
    op.drop_table("predictions")
    op.drop_table("xrays")
    op.drop_table("doctors")
    op.drop_table("patients")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS xray_status")
    op.execute("DROP TYPE IF EXISTS user_role")
