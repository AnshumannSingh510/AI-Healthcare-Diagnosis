import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.xray import Xray, XrayStatus
from app.models.prediction import Prediction
from app.core.security import get_current_user, require_roles
from app.core.config import settings
from app.schemas.prediction import XrayUploadResponse, XrayStatusResponse, PredictionResponse
from app.services.storage import save_upload
from app.workers.tasks import run_inference_task

router = APIRouter(tags=["xray"])

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}


@router.post("/xray/upload", response_model=XrayUploadResponse)
def upload_xray(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.patient.value, UserRole.admin.value])),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PNG/JPEG images are accepted")

    file_bytes = file.file.read()
    if len(file_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 15MB)")

    stored_path = save_upload(file_bytes, file.filename)

    xray = Xray(patient_id=current_user.id, image_path=stored_path, status=XrayStatus.uploaded)
    db.add(xray)
    db.commit()
    db.refresh(xray)

    # Enqueue async Celery task: inference -> gradcam -> explanation -> DB write
    run_inference_task.delay(str(xray.id))

    return XrayUploadResponse(
        xray_id=xray.id, status=xray.status.value, message="X-ray uploaded and queued for analysis."
    )


@router.get("/xray/{xray_id}/status", response_model=XrayStatusResponse)
def xray_status(xray_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    xray = db.query(Xray).filter(Xray.id == xray_id).first()
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")
    if current_user.role == UserRole.patient and xray.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this x-ray")

    prediction = db.query(Prediction).filter(Prediction.xray_id == xray.id).first()
    return XrayStatusResponse(
        xray_id=xray.id, status=xray.status.value, prediction_id=prediction.id if prediction else None
    )


def _prediction_to_response(pred: Prediction) -> PredictionResponse:
    recs = pred.recommendation.split("\n") if pred.recommendation else []
    return PredictionResponse(
        id=pred.id,
        xray_id=pred.xray_id,
        disease=pred.disease,
        confidence=pred.confidence,
        all_scores=pred.all_scores,
        heatmap_path=pred.heatmap_path,
        severity=pred.severity,
        recommendation=recs,
        ai_explanation=pred.ai_explanation,
        disclaimer=settings.DISCLAIMER,
        notes=pred.notes,
        created_at=pred.created_at,
    )


@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
def get_prediction(prediction_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    xray = db.query(Xray).filter(Xray.id == pred.xray_id).first()
    if current_user.role == UserRole.patient and xray.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return _prediction_to_response(pred)


@router.get("/patients/{patient_id}/history", response_model=list[PredictionResponse])
def patient_history(patient_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.patient and current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    # Doctors are permitted; a stricter implementation would also verify assignment here.

    xray_ids = [x.id for x in db.query(Xray).filter(Xray.patient_id == patient_id).all()]
    preds = db.query(Prediction).filter(Prediction.xray_id.in_(xray_ids)).order_by(Prediction.created_at.desc()).all()
    return [_prediction_to_response(p) for p in preds]
