import uuid
import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel


class XrayUploadResponse(BaseModel):
    xray_id: uuid.UUID
    status: str
    message: str


class XrayStatusResponse(BaseModel):
    xray_id: uuid.UUID
    status: str
    prediction_id: Optional[uuid.UUID] = None


class PredictionResponse(BaseModel):
    id: uuid.UUID
    xray_id: uuid.UUID
    disease: str
    confidence: float
    all_scores: Optional[Dict[str, float]] = None
    heatmap_path: Optional[str] = None
    severity: Optional[str] = None
    recommendation: Optional[List[str]] = None
    ai_explanation: Optional[str] = None
    disclaimer: str
    notes: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class DoctorReviewRequest(BaseModel):
    notes: Optional[str] = None
    approve: bool = False
    doctor_comment: Optional[str] = None
