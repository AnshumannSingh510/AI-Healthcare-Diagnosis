import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=False, index=True)
    doctor_comment = Column(Text, nullable=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved = Column(Boolean, nullable=False, default=False)
    pdf_path = Column(String(512), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
