"""
File storage abstraction. Currently backed by the local filesystem, but the
function signatures are written so this module can be swapped for an
S3-backed implementation (boto3 put_object/get_object) later without
changing any callers.
"""
import os
import uuid
from pathlib import Path

from app.core.config import settings

for _dir in (settings.UPLOAD_DIR, settings.HEATMAP_DIR, settings.REPORT_DIR):
    os.makedirs(_dir, exist_ok=True)


def save_upload(file_bytes: bytes, original_filename: str) -> str:
    """Save an uploaded xray image, return the storage path."""
    ext = Path(original_filename).suffix or ".png"
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path


def heatmap_path_for(xray_id: str) -> str:
    return os.path.join(settings.HEATMAP_DIR, f"{xray_id}_heatmap.png")


def report_path_for(prediction_id: str) -> str:
    return os.path.join(settings.REPORT_DIR, f"{prediction_id}_report.pdf")


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
