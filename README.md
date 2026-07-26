# AI-Powered Healthcare Diagnosis Platform

Chest X-ray disease detection and clinical decision support — a full-stack
prototype combining a PyTorch DenseNet121 model (with Grad-CAM
explainability), a FastAPI backend, a React frontend, async inference via
Celery/Redis, PDF report generation, and a medical chatbot.

> ⚠️ **This is a clinical decision-support prototype, not an approved
> medical device.** No prediction, chatbot answer, or report should be
> treated as a confirmed diagnosis. Every AI output carries a visible
> disclaimer to consult a licensed physician.

## Project layout

```
healthcare-ai/
├── frontend/       React + Tailwind app
├── backend/        FastAPI app (routers, services, models, schemas, Celery workers)
├── model/          PyTorch training, inference, Grad-CAM code, saved weights
├── dataset/        Dataset prep scripts + instructions for NIH ChestX-ray14 / CheXpert
├── docs/           Architecture notes, API reference, deployment guide
├── docker-compose.yml
└── README.md        (this file)
```

## Prerequisites

- Docker + Docker Compose
- (Optional, for local non-Docker development) Python 3.11+, Node.js 20+

## 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `JWT_SECRET` — any long random string for local dev (`openssl rand -hex 32`)
- `LLM_PROVIDER` / `LLM_API_KEY` — optional; leave `LLM_PROVIDER=none` to run
  the chatbot and AI-explanation generator on deterministic template
  responses with **no API key required**.

Also copy the frontend env file if running the frontend outside Docker:
```bash
cp frontend/.env.example frontend/.env
```

## 2. Run the full stack with Docker Compose

```bash
docker-compose up --build
```

This starts:
- `postgres` — PostgreSQL 16, with a persistent volume
- `redis` — broker/result backend for Celery
- `backend` — FastAPI + Uvicorn on `http://localhost:8000` (runs Alembic
  migrations automatically on startup via `backend/entrypoint.sh`)
- `worker` — Celery worker running the async inference pipeline
- `frontend` — React app built and served via nginx on `http://localhost:3000`

Once running:
- Frontend: http://localhost:3000
- Backend API docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## 3. Database migrations

Migrations run automatically when the `backend` container starts
(`alembic upgrade head`, see `backend/entrypoint.sh`). To run them manually:

```bash
docker-compose exec backend alembic upgrade head
```

To create a new migration after changing SQLAlchemy models:

```bash
docker-compose exec backend alembic revision --autogenerate -m "describe change"
docker-compose exec backend alembic upgrade head
```

## 4. Dataset & model training

The app runs end-to-end **without training a model first** — `model/predict.py`
falls back to an ImageNet-pretrained DenseNet121 with an untrained
classification head, so predictions are structurally valid but not
clinically meaningful until you train on real data.

To train a real model:

1. Follow `dataset/README.md` to download NIH ChestX-ray14 or CheXpert and
   build a training manifest:
   ```bash
   python dataset/build_manifest.py --source nih \
     --csv dataset/raw/nih/Data_Entry_2017.csv \
     --image_dir dataset/raw/nih/images \
     --output_train dataset/train.csv --output_val dataset/val.csv
   ```
2. Train (requires the `model/requirements.txt` deps installed, ideally with
   a GPU available):
   ```bash
   pip install -r model/requirements.txt
   python -m model.train --train_csv dataset/train.csv --val_csv dataset/val.csv \
     --image_root dataset/raw/nih --epochs 30 --backbone densenet121
   ```
3. The best checkpoint is saved to `model/weights/densenet121_chest.pt`.
   Copy it into the running backend/worker containers' `model_weights`
   volume so the app picks it up:
   ```bash
   docker cp model/weights/densenet121_chest.pt \
     $(docker-compose ps -q backend):/app/model_weights/densenet121_chest.pt
   docker cp model/weights/densenet121_chest.pt \
     $(docker-compose ps -q worker):/app/model_weights/densenet121_chest.pt
   docker-compose restart backend worker
   ```

## 5. Using the app end-to-end

1. Open http://localhost:3000, click **Get started**, register as a
   **patient** (or **doctor**).
2. As a patient: **Upload X-ray** → drag/drop a PNG or JPEG chest X-ray →
   the app polls processing status → redirects to the **Diagnosis Result**
   page with disease prediction, confidence, Grad-CAM heatmap, AI
   explanation, severity, and clinical recommendations.
3. Download a PDF report directly from the result page, or from
   **Reports** in the nav.
4. As a doctor (after an admin/DB update assigns a patient to you via
   `patients.assigned_doctor_id`): open **Dashboard** → select a patient →
   review their scans, add notes, and **Approve & Generate Report**.
5. Use **AI Chat** for general, non-diagnostic questions — answers always
   include a disclaimer to consult a licensed physician.

> Note: the MVP has no admin UI for assigning patients to doctors yet.
> Assign a patient to a doctor directly in the database for local testing:
> ```sql
> UPDATE patients SET assigned_doctor_id = '<doctor user id>' WHERE patient_id = '<patient user id>';
> ```

## 6. Running components individually (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare_ai
alembic upgrade head
uvicorn app.main:app --reload
```

**Celery worker:**
```bash
cd backend
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, async
  pipeline, explainability, and clinical rules design
- [`docs/API.md`](docs/API.md) — full endpoint reference
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — recommended production
  deployment targets (Vercel, Render/Railway, Hugging Face Spaces)
- [`dataset/README.md`](dataset/README.md) — dataset download and manifest
  preparation

## MVP feature checklist

- [x] User registration and login (JWT, role-based)
- [x] Chest X-ray image upload
- [x] AI disease prediction (DenseNet121)
- [x] Grad-CAM visualization
- [x] Prediction confidence score
- [x] Rule-based clinical recommendations
- [x] Prediction history
- [x] Doctor review workflow
- [x] PDF report generation
- [x] AI medical chatbot with disclaimer
- [x] Responsive React interface
- [x] FastAPI backend with routers/services/schemas separation
- [x] PostgreSQL database with Alembic migrations
- [x] Docker Compose to run the entire stack with one command

## License / disclaimer

This project is a prototype for educational and demonstration purposes. It
is **not** an FDA-approved or CE-marked medical device, and must not be used
for real clinical decision-making without appropriate regulatory clearance,
clinical validation, and human oversight.
