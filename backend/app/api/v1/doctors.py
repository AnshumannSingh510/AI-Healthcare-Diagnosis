import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.clinical import Patient
from app.models.prediction import Prediction
from app.models.xray import Xray
from app.core.security import require_roles
from app.schemas.auth import UserResponse
from app.schemas.prediction import DoctorReviewRequest, PredictionResponse
from app.core.config import settings

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_id}/patients", response_model=list[UserResponse])
def list_assigned_patients(
    doctor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.doctor.value, UserRole.admin.value])),
):
    if current_user.role == UserRole.doctor and current_user.id != doctor_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    patients = db.query(Patient).filter(Patient.assigned_doctor_id == doctor_id).all()
    return [p.user for p in patients]


@router.post("/predictions/{prediction_id}/review", response_model=PredictionResponse)
def review_prediction(
    prediction_id: uuid.UUID,
    payload: DoctorReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.doctor.value, UserRole.admin.value])),
):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    xray = db.query(Xray).filter(Xray.id == pred.xray_id).first()
    patient = db.query(Patient).filter(Patient.patient_id == xray.patient_id).first()
    if current_user.role == UserRole.doctor and (
        not patient or patient.assigned_doctor_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not authorized to review this patient's data")

    if payload.notes is not None:
        pred.notes = payload.notes
    db.commit()
    db.refresh(pred)

    recs = pred.recommendation.split("\n") if pred.recommendation else []
    return PredictionResponse(
        id=pred.id, xray_id=pred.xray_id, disease=pred.disease, confidence=pred.confidence,
        all_scores=pred.all_scores, heatmap_path=pred.heatmap_path, severity=pred.severity,
        recommendation=recs, ai_explanation=pred.ai_explanation, disclaimer=settings.DISCLAIMER,
        notes=pred.notes, created_at=pred.created_at,
    )
