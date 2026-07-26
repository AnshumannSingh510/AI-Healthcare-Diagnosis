FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt

# Install CPU-only PyTorch wheels from the official PyTorch CPU index.
# The default PyPI torch build pulls in ~2GB of NVIDIA CUDA packages that
# are unused for CPU inference — this cuts the download to ~200-300MB and
# avoids multi-hour downloads on slower connections.
RUN pip install --no-cache-dir torch==2.3.0+cpu torchvision==0.18.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

# Backend app code
COPY backend /app

# The `model` package (dataset/train/gradcam/predict/explain) is imported
# by the backend's Celery tasks and the sync /predict endpoint.
COPY model /app/model

ENV PYTHONPATH=/app
ENV MODEL_WEIGHTS_PATH=/app/model_weights/densenet121_chest.pt

RUN mkdir -p /app/storage/uploads /app/storage/heatmaps /app/storage/reports /app/model_weights

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
