# Deployment Guide

This document describes recommended production deployment targets. It is
documentation only — the Docker Compose setup in this repo is intended for
**local development**, not production infrastructure.

## Recommended targets

| Layer | Recommended service |
|---|---|
| Frontend (React static build) | Vercel |
| Backend (FastAPI) | Render or Railway |
| Database (PostgreSQL) | Railway PostgreSQL (or Render Postgres) |
| Model inference (GPU) | Hugging Face Spaces (GPU tier) or any GPU-enabled compute service |
| Redis / Celery broker | Render Redis or Railway Redis add-on |

## 1. Frontend → Vercel

1. Push this repo to GitHub.
2. In Vercel, "Import Project" → select the repo, set **Root Directory** to
   `frontend`.
3. Framework preset: Vite. Build command `npm run build`, output directory `dist`.
4. Set environment variables in Vercel's dashboard:
   - `VITE_API_BASE_URL=https://<your-backend-domain>/api/v1`
   - `VITE_STORAGE_BASE_URL=https://<your-backend-domain>/storage`
5. Deploy. Vercel will auto-redeploy on pushes to `main`.

## 2. Backend → Render or Railway

1. Create a new **Web Service** pointing at this repo, root directory `backend`
   (or use the provided `backend/Dockerfile` directly if the platform supports
   Docker deploys, which is the simplest path since it bundles the `model/`
   package correctly).
2. Set environment variables from `.env.example` (`DATABASE_URL`, `JWT_SECRET`,
   `REDIS_URL`, `LLM_API_KEY`, `MODEL_WEIGHTS_PATH`, etc.), pointing
   `DATABASE_URL` and `REDIS_URL` at your managed Postgres/Redis instances.
3. Add a **Background Worker** service using `backend/Dockerfile.worker` for
   the Celery worker, pointed at the same `DATABASE_URL` / `REDIS_URL`.
4. Run `alembic upgrade head` as a release/start command (the provided
   `backend/entrypoint.sh` already does this automatically on container start).
5. Mount or attach persistent storage for `/app/storage` and
   `/app/model_weights` (or swap `app/services/storage.py` for an S3-backed
   implementation — it was written with that swap in mind).

## 3. Database → Railway PostgreSQL

1. Provision a PostgreSQL instance in Railway (or Render Postgres).
2. Copy the connection string into your backend's `DATABASE_URL` env var,
   in the form `postgresql+psycopg2://user:pass@host:port/dbname`.
3. Ensure the backend service has network access to the database (same
   Railway project, or Render's private networking).

## 4. Model inference → Hugging Face Spaces or GPU-enabled service

For higher-throughput or lower-latency inference than CPU containers allow:

1. Package `model/predict.py` + `model/weights/densenet121_chest.pt` as a
   Hugging Face Space (Gradio or FastAPI SDK) or a small FastAPI service on
   a GPU-enabled host (e.g. a GPU instance on Railway/Render/Modal/Replicate).
2. Point the backend's Celery task (`backend/app/workers/tasks.py`) at this
   remote inference endpoint instead of calling `model.predict.predict_image`
   in-process — swap the direct function call for an HTTP request to the
   inference service, keeping the rest of the pipeline (clinical rules,
   explanation, DB write) unchanged.

## Secrets checklist before going to production

- [ ] Rotate `JWT_SECRET` to a long random value (`openssl rand -hex 32`)
- [ ] Set a real `LLM_API_KEY` and `LLM_PROVIDER` if the chatbot/explanations
      should use a real LLM instead of the template fallback
- [ ] Restrict `CORS_ORIGINS` to your actual frontend domain
- [ ] Switch file storage from local disk to S3 (or equivalent) for durability
- [ ] Put the backend behind HTTPS (Render/Railway provide this by default)
- [ ] Review and tighten Postgres network access rules
