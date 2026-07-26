"""
Given a prediction (disease, confidence, severity), produce a plain-language
explanation of what the finding means and what the highlighted Grad-CAM
region typically indicates. Uses the backend's LLM client if available,
falling back to a deterministic template otherwise, so this module works
standalone (e.g. when called from the Celery worker) without importing
FastAPI internals directly.
"""
from typing import Callable, Awaitable

REGION_HINTS = {
    "Pneumonia": "areas of increased opacity (whiteness) in the lung fields, often clustered in one lobe",
    "Cardiomegaly": "the heart's silhouette appearing enlarged relative to the chest cavity",
    "Fibrosis": "streaky or net-like patterns in the lower lung zones",
    "Edema": "hazy, diffuse opacities spreading from the central lung areas outward",
    "Effusion": "blunting at the bottom corners of the lung fields, suggesting fluid buildup",
    "Atelectasis": "a collapsed or airless-looking segment of lung tissue",
    "Nodule": "a small, rounded spot within the lung tissue",
    "Mass": "a larger, irregular area of density within the lung tissue",
    "Pneumothorax": "an area lacking normal lung markings, suggesting air outside the lung",
    "Normal": "no significant abnormal opacities or structural irregularities",
}


def _template_explanation(disease: str, confidence: float, severity: str) -> str:
    region = REGION_HINTS.get(disease, "the highlighted region of the image")
    pct = f"{confidence * 100:.1f}%"

    if disease == "Normal":
        return (
            f"The AI model did not detect strong indicators of common chest abnormalities "
            f"in this X-ray (confidence: {pct}). The highlighted regions show {region}. "
            "This is a screening result, not a clinical clearance — please continue routine "
            "checkups as advised by your physician."
        )

    return (
        f"The AI model flagged this X-ray as showing patterns consistent with {disease} "
        f"(confidence: {pct}, severity band: {severity}). "
        f"The Grad-CAM heatmap highlights {region}, which is the region the model weighted "
        "most heavily when making this prediction. This is an AI-generated pattern match, "
        "not a confirmed diagnosis — a licensed physician should review the image and your "
        "clinical history before any treatment decision is made."
    )


async def build_explanation(
    disease: str,
    confidence: float,
    severity: str,
    llm_fn: Callable[..., Awaitable[str]] = None,
) -> str:
    """
    llm_fn: optional async callable(prompt: str) -> str, typically
    app.services.llm_client.generate_response, injected by the caller to
    avoid a hard dependency of the `model` package on the backend app.
    """
    template = _template_explanation(disease, confidence, severity)

    if llm_fn is None:
        return template

    prompt = (
        f"A chest X-ray AI model predicted the finding '{disease}' with confidence "
        f"{confidence * 100:.1f}% (severity band: {severity}). "
        "Explain in 3-4 simple sentences, for a patient with no medical background, what this "
        "finding generally means and what part of the lungs is typically involved. "
        "Do not give a definitive diagnosis. End with a reminder to consult a licensed physician."
    )
    try:
        return await llm_fn(prompt)
    except Exception:
        return template
