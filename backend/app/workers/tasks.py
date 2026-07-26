"""
Celery tasks wiring the async pipeline:
  upload (already done in API) -> inference -> Grad-CAM -> AI explanation -> DB write

Also exposes run_inference_sync() for synchronous local testing without a
running Celery worker (used by the /predict endpoint).
"""
import asyncio

from app.workers.celery_app import celery_app
from app.db.session import SessionLocal

# Import ALL model modules here (not just the ones this file uses directly).
# SQLAlchemy only registers a table in Base.metadata once its model class is
# imported somewhere in the process. The worker is a separate process from
# the FastAPI backend, so relying on another module having imported User,
# Report, etc. is not safe -- every model must be imported explicitly in
# any process that runs queries or resolves relationships/foreign keys.
from app.models import user, clinical, xray, prediction, report, chat  # noqa: F401
from app.models.xray import Xray, XrayStatus
from app.models.prediction import Prediction
from app.services.clinical_rules import evaluate
from app.services.storage import heatmap_path_for
from app.services.llm_client import generate_response

# The `model` package lives at repo-root /model and is added to PYTHONPATH
# in the worker/backend Dockerfiles (see docker-compose.yml + Dockerfiles).
from model.predict import predict_image
from model.explain import build_explanation


def _run_pipeline(xray_id: str) -> dict:
    db = SessionLocal()
    try:
        xray = db.query(Xray).filter(Xray.id == xray_id).first()
        if not xray:
            raise ValueError(f"Xray {xray_id} not found")

        xray.status = XrayStatus.processing
        db.commit()

        heatmap_out = heatmap_path_for(str(xray.id))

        # 1. Run model inference + Grad-CAM
        result = predict_image(image_path=xray.image_path, heatmap_output_path=heatmap_out)
        # result: {"disease": str, "confidence": float, "all_scores": {label: score}, "heatmap_path": str}

        # 2. Rule-based clinical decision support
        clinical = evaluate(result["disease"], result["confidence"])

        # 3. Plain-language AI explanation (LLM if configured, else template)
        explanation = asyncio.run(
            build_explanation(
                disease=result["disease"],
                confidence=result["confidence"],
                severity=clinical["severity"],
                llm_fn=generate_response,
            )
        )

        # 4. Persist prediction
        prediction = Prediction(
            xray_id=xray.id,
            disease=result["disease"],
            confidence=result["confidence"],
            all_scores=result.get("all_scores"),
            heatmap_path=result["heatmap_path"],
            severity=clinical["severity"],
            recommendation="\n".join(clinical["recommendation"]),
            ai_explanation=explanation,
        )
        db.add(prediction)

        xray.status = XrayStatus.completed
        db.commit()
        db.refresh(prediction)

        return {
            "xray_id": str(xray.id),
            "prediction_id": str(prediction.id),
            "disease": prediction.disease,
            "confidence": prediction.confidence,
            "severity": prediction.severity,
        }
    except Exception as exc:
        db.rollback()
        xray = db.query(Xray).filter(Xray.id == xray_id).first()
        if xray:
            xray.status = XrayStatus.failed
            db.commit()
        raise exc
    finally:
        db.close()


@celery_app.task(name="run_inference_task", bind=True, max_retries=2)
def run_inference_task(self, xray_id: str) -> dict:
    return _run_pipeline(xray_id)


def run_inference_sync(xray_id: str) -> dict:
    """Direct synchronous call, e.g. for the /predict testing endpoint."""
    return _run_pipeline(xray_id)
