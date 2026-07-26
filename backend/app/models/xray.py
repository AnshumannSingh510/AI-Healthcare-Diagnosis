import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class XrayStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Xray(Base):
    __tablename__ = "xrays"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    image_path = Column(String(512), nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(XrayStatus, name="xray_status"), nullable=False, default=XrayStatus.uploaded)
