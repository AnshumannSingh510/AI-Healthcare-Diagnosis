"""
Rule-based Clinical Decision Support module.

Given a predicted disease label and a confidence score, this module derives:
  - a severity band (Mild/Uncertain, Moderate, High Confidence)
  - a list of recommended next clinical steps
  - a mandatory disclaimer

This is intentionally rule-based (not learned) so that its behavior is
transparent, auditable, and easy for a clinician to review/override.
"""
from typing import List, TypedDict

from app.core.config import settings

DISCLAIMER = settings.DISCLAIMER

# Confidence bands
LOW_CONF_THRESHOLD = 0.70
HIGH_CONF_THRESHOLD = 0.90


class ClinicalResult(TypedDict):
    disease: str
    confidence: float
    severity: str
    recommendation: List[str]
    disclaimer: str


# Per-disease recommendation templates. Each entry is a base set of
# recommendations; severity band may add extra urgency notes.
DISEASE_RULES = {
    "Normal": {
        "base": [
            "No acute radiographic abnormality detected.",
            "Continue routine health checkups.",
            "Maintain healthy lifestyle and periodic screening as advised by your physician.",
        ],
    },
    "Pneumonia": {
        "base": [
            "Consult a Pulmonologist or General Physician promptly.",
            "Blood test (CBC, CRP) recommended.",
            "Consider sputum culture if symptoms persist.",
            "Follow prescribed antibiotics course if bacterial infection is confirmed.",
            "Follow-up chest X-ray after 7-10 days.",
        ],
    },
    "Cardiomegaly": {
        "base": [
            "Consult a Cardiologist for further evaluation.",
            "Echocardiogram recommended to assess cardiac function.",
            "Monitor blood pressure and review medication history.",
        ],
    },
    "Fibrosis": {
        "base": [
            "Consult a Pulmonologist.",
            "High-resolution CT (HRCT) chest recommended for confirmation.",
            "Pulmonary function tests (PFTs) advised.",
        ],
    },
    "Edema": {
        "base": [
            "Consult a Cardiologist or Pulmonologist urgently.",
            "Assess for congestive heart failure (BNP levels, echocardiogram).",
            "Monitor fluid balance and oxygen saturation.",
        ],
    },
    "Effusion": {
        "base": [
            "Consult a Pulmonologist.",
            "Ultrasound-guided thoracentesis may be considered if clinically indicated.",
            "Evaluate underlying cause (infection, heart failure, malignancy).",
        ],
    },
    "Atelectasis": {
        "base": [
            "Consult a Pulmonologist.",
            "Encourage deep breathing exercises / incentive spirometry.",
            "Evaluate for underlying airway obstruction if persistent.",
        ],
    },
    "Nodule": {
        "base": [
            "Consult a Pulmonologist or Radiologist for further characterization.",
            "Follow-up CT chest recommended to assess nodule size/growth.",
            "Compare with prior imaging if available.",
        ],
    },
    "Mass": {
        "base": [
            "Urgent consultation with a Pulmonologist/Oncologist recommended.",
            "CT chest with contrast advised for further characterization.",
            "Consider biopsy per specialist evaluation.",
        ],
    },
    "Pneumothorax": {
        "base": [
            "Seek immediate medical attention — this may be a medical emergency.",
            "Confirm with clinical exam and repeat imaging.",
            "Chest tube placement may be required depending on severity.",
        ],
    },
}

DEFAULT_RULES = {
    "base": [
        "Consult a licensed physician to review this finding.",
        "Correlate with clinical symptoms and history.",
    ]
}


def _severity_from_confidence(confidence: float) -> str:
    if confidence < LOW_CONF_THRESHOLD:
        return "Mild / Uncertain"
    elif confidence < HIGH_CONF_THRESHOLD:
        return "Moderate"
    else:
        return "High Confidence"


def evaluate(disease: str, confidence: float) -> ClinicalResult:
    """
    Main entry point: given a disease label and confidence (0-1 float),
    return a structured clinical decision support object.
    """
    confidence = max(0.0, min(1.0, float(confidence)))
    rules = DISEASE_RULES.get(disease, DEFAULT_RULES)
    severity = _severity_from_confidence(confidence)

    recommendations = list(rules["base"])

    # Add severity-driven urgency notes
    if severity == "Mild / Uncertain":
        recommendations.append(
            "Confidence is low — consider repeat imaging or additional clinical correlation."
        )
    elif severity == "High Confidence" and disease not in ("Normal",):
        recommendations.append(
            "Finding shows high model confidence — prioritize clinical follow-up."
        )

    return {
        "disease": disease,
        "confidence": round(confidence, 4),
        "severity": severity,
        "recommendation": recommendations,
        "disclaimer": DISCLAIMER,
    }


def evaluate_multilabel(scores: dict, top_k: int = 3) -> List[ClinicalResult]:
    """
    For multi-label predictions (a dict of disease -> confidence), return
    clinical decision-support results for the top_k most confident findings.
    """
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [evaluate(disease, conf) for disease, conf in ranked]
