# Architecture Notes

## High-level flow

```
Patient (React frontend)
   │  1. Upload chest X-ray (multipart/form-data)
   ▼
FastAPI backend  ──►  saves file to /app/storage/uploads
   │  2. Creates `xrays` row (status=uploaded)
   │  3. Enqueues Celery task `run_inference_task(xray_id)`
   ▼
Redis (broker)
   ▼
Celery worker
   │  4. Loads DenseNet121 model + weights
   │  5. Runs forward pass → per-class sigmoid confidence scores
   │  6. Runs Grad-CAM on the top predicted class → heatmap PNG
   │  7. Runs rule-based Clinical Decision Support (severity + recommendations)
   │  8. Requests a plain-language AI explanation (LLM or template fallback)
   │  9. Writes `predictions` row, sets `xrays.status = completed`
   ▼
Frontend polls GET /api/v1/xray/{id}/status until completed
   │  10. Fetches GET /api/v1/predictions/{id}
   ▼
Doctor reviews (adds notes, approves) ──► POST /api/v1/reports/{id}/generate
   │  11. ReportLab renders a PDF (X-ray + heatmap + explanation + disclaimer)
   ▼
Patient/doctor downloads PDF via GET /api/v1/reports/{id}
```

## Why async (Celery + Redis) for inference?

Model inference (even on CPU) can take a few seconds, and Grad-CAM requires
an extra backward pass. Running this synchronously inside the HTTP request
would block the API worker and hurt throughput under concurrent uploads.
The upload endpoint returns immediately with `status=uploaded`, and the
frontend polls `/xray/{id}/status` (a WebSocket push is a natural future
upgrade — see `frontend/src/hooks/useWebSocket.js`, which is structured so
polling can be swapped for a real WebSocket subscription without changing
the component API).

## Why a separate `model/` package?

`model/` is intentionally decoupled from `backend/app/` so that:
- Data scientists can iterate on `train.py` / `dataset.py` without touching
  API code.
- The same package is imported by both the FastAPI backend (for the
  synchronous `/predict` testing endpoint) and the Celery worker (for the
  async pipeline), avoiding duplicated inference logic.
- It could later be extracted into its own microservice/container (e.g. a
  GPU-backed inference server) with minimal changes to `predict.py`'s
  function signature.

## Explainability

`model/gradcam.py` implements Grad-CAM against the last dense block of
DenseNet121 (`features.denseblock4`). The resulting class activation map is
resized to the original image resolution and alpha-blended over the
original X-ray using OpenCV's `COLORMAP_JET`, producing an intuitive
red/yellow = high-attention, blue = low-attention overlay.

## Clinical Decision Support

`backend/app/services/clinical_rules.py` is deliberately a plain Python
rules table, not a model. Severity bands are derived purely from the
model's confidence score:
- `< 70%` → Mild / Uncertain
- `70–90%` → Moderate
- `> 90%` → High Confidence

Recommendations are static per-disease lists augmented with a severity-based
note. This keeps the decision-support logic auditable and easy for a
clinician to review/extend, independent of the underlying ML model.

## Auth & permissions model

JWT access + refresh tokens carry `sub` (user id) and `role`. FastAPI
dependencies (`get_current_user`, `require_roles`) enforce role checks at
the route level; ownership checks (e.g. "is this patient's own data") are
enforced inside each route handler by comparing `current_user.id` /
`current_user.role` against the resource's owner/assignment.

## Data flow for multi-label vs single-label

The model outputs a sigmoid confidence per disease class (multi-label). The
API currently surfaces the single top-confidence disease as the primary
`disease`/`confidence` fields on `Prediction`, while `all_scores` retains
the full per-class map. `clinical_rules.evaluate_multilabel()` is available
for surfacing multiple concurrent findings if the frontend is extended to
show more than the top prediction.
