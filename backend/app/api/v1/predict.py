import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.xray import Xray, XrayStatus
from app.core.security import get_current_user
from app.workers.tasks import run_inference_sync

router = APIRouter(tags=["predict"])


@router.post("/predict")
def predict_now(xray_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Synchronous inference trigger, primarily for local testing/dev without
    needing the Celery worker running. Production uploads use the async
    Celery pipeline (see /xray/upload).
    """
    xray = db.query(Xray).filter(Xray.id == xray_id).first()
    if not xray:
        raise HTTPException(status_code=404, detail="X-ray not found")

    result = run_inference_sync(str(xray.id))
    return result
