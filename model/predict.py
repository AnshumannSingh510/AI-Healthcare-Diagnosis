"""
Inference pipeline used by the backend Celery worker (and the sync /predict
testing endpoint).

predict_image(image_path, heatmap_output_path) ->
    {
        "disease": <top predicted label>,
        "confidence": <float 0-1>,
        "all_scores": {label: float, ...},
        "heatmap_path": <path to saved Grad-CAM overlay PNG>,
    }
"""
import os
import functools

import cv2
import numpy as np
import torch
from PIL import Image

from model.architecture import build_model
from model.gradcam import GradCAM, find_densenet_target_layer, overlay_heatmap_on_image
from model.dataset import build_transforms
from model.labels import DISEASE_LABELS

MODEL_WEIGHTS_PATH = os.environ.get("MODEL_WEIGHTS_PATH", "/app/model_weights/densenet121_chest.pt")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@functools.lru_cache(maxsize=1)
def _load_model():
    """
    Lazily load and cache the model + weights (once per worker process).
    If no trained checkpoint exists yet, falls back to an ImageNet-pretrained
    DenseNet121 with a randomly-initialized classification head, so the
    pipeline is runnable end-to-end even before training is complete.
    """
    model = build_model("densenet121", pretrained=True, num_classes=len(DISEASE_LABELS))

    if os.path.exists(MODEL_WEIGHTS_PATH):
        checkpoint = torch.load(MODEL_WEIGHTS_PATH, map_location=DEVICE)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        model.load_state_dict(state_dict)
        print(f"Loaded trained weights from {MODEL_WEIGHTS_PATH}")
    else:
        print(
            f"WARNING: No trained weights found at {MODEL_WEIGHTS_PATH}. "
            "Using ImageNet-pretrained backbone with an untrained classifier head. "
            "Predictions will not be clinically meaningful until the model is trained "
            "(see model/train.py)."
        )

    model.to(DEVICE)
    model.eval()
    return model


def predict_image(image_path: str, heatmap_output_path: str, top_k: int = 1) -> dict:
    model = _load_model()
    transform = build_transforms(train=False)

    pil_image = Image.open(image_path).convert("RGB")
    input_tensor = transform(pil_image).unsqueeze(0).to(DEVICE)
    input_tensor.requires_grad_(False)

    with torch.no_grad():
        logits = model(input_tensor)
        probs = torch.sigmoid(logits).squeeze(0).cpu().numpy()

    all_scores = {label: float(probs[i]) for i, label in enumerate(DISEASE_LABELS)}
    top_idx = int(np.argmax(probs))
    top_label = DISEASE_LABELS[top_idx]
    top_confidence = float(probs[top_idx])

    # Grad-CAM needs gradients, so re-run forward pass with grad enabled
    target_layer = find_densenet_target_layer(model)
    cam_generator = GradCAM(model, target_layer)
    input_tensor_grad = transform(pil_image).unsqueeze(0).to(DEVICE)
    input_tensor_grad.requires_grad_(True)
    cam = cam_generator.generate(input_tensor_grad, class_idx=top_idx)

    original_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    os.makedirs(os.path.dirname(heatmap_output_path), exist_ok=True)
    overlay_heatmap_on_image(original_bgr, cam, heatmap_output_path)

    return {
        "disease": top_label,
        "confidence": top_confidence,
        "all_scores": all_scores,
        "heatmap_path": heatmap_output_path,
    }
