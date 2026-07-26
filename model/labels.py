"""
Disease label set used across dataset loading, training, and inference.
Matches the classes handled by the clinical decision-support rules table
(backend/app/services/clinical_rules.py) plus "Normal".

Based on the NIH ChestX-ray14 label taxonomy (a subset relevant to the
clinical rules we implement). Extend as needed for CheXpert's 14 labels.
"""

DISEASE_LABELS = [
    "Normal",
    "Pneumonia",
    "Cardiomegaly",
    "Fibrosis",
    "Edema",
    "Effusion",
    "Atelectasis",
    "Nodule",
    "Mass",
    "Pneumothorax",
]

NUM_CLASSES = len(DISEASE_LABELS)
LABEL_TO_IDX = {label: i for i, label in enumerate(DISEASE_LABELS)}
IDX_TO_LABEL = {i: label for label, i in LABEL_TO_IDX.items()}
