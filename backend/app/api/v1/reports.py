import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.prediction import Prediction
from app.models.xray import Xray
from app.models.clinical import Patient
from app.models.report import Report
from app.core.security import get_current_user, require_roles
from app.schemas.chat import ReportGenerateResponse
from app.services.storage import report_path_for
from app.services.pdf_report import build_report_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{prediction_id}/generate", response_model=ReportGenerateResponse)
def generate_report(
    prediction_id: uuid.UUID,
    doctor_comment: str = None,
    approve: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    xray = db.query(Xray).filter(Xray.id == pred.xray_id).first()
    if current_user.role == UserRole.patient and xray.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    patient_record = db.query(Patient).filter(Patient.patient_id == xray.patient_id).first()
    patient_user = patient_record.user if patient_record else None

    if approve and current_user.role not in (UserRole.doctor, UserRole.admin):
        raise HTTPException(status_code=403, detail="Only a doctor can approve a report")

    recs = pred.recommendation.split("\n") if pred.recommendation else []
    output_path = report_path_for(str(pred.id))

    build_report_pdf(
        output_path=output_path,
        patient_name=patient_user.name if patient_user else "Unknown",
        patient_age=patient_record.age if patient_record else None,
        patient_gender=patient_record.gender if patient_record else None,
        xray_image_path=xray.image_path,
        heatmap_image_path=pred.heatmap_path,
        disease=pred.disease,
        confidence=pred.confidence,
        severity=pred.severity,
        recommendations=recs,
        ai_explanation=pred.ai_explanation,
        doctor_comment=doctor_comment,
        approved=approve,
    )

    report = Report(
        prediction_id=pred.id,
        doctor_comment=doctor_comment,
        doctor_id=current_user.id if current_user.role in (UserRole.doctor, UserRole.admin) else None,
        approved=approve,
        pdf_path=output_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportGenerateResponse(id=report.id, pdf_path=report.pdf_path, generated_at=report.generated_at)


@router.get("/{report_id}")
def download_report(report_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"report_{report.id}.pdf")
