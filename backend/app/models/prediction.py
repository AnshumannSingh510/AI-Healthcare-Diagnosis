import uuid
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    xray_id = Column(UUID(as_uuid=True), ForeignKey("xrays.id"), nullable=False, index=True)
    disease = Column(String(255), nullable=False)          # top predicted label
    confidence = Column(Float, nullable=False)              # top predicted confidence
    all_scores = Column(JSON, nullable=True)                # per-class confidence map
    heatmap_path = Column(String(512), nullable=True)
    severity = Column(String(32), nullable=True)
    recommendation = Column(Text, nullable=True)             # newline-joined recommendations
    ai_explanation = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
