"""
PyTorch Dataset for chest X-ray images with multi-label targets.

Expects a CSV manifest with columns:
    image_path, Normal, Pneumonia, Cardiomegaly, Fibrosis, Edema, Effusion,
    Atelectasis, Nodule, Mass, Pneumothorax
where each disease column is 0/1 (multi-label; NIH ChestX-ray14 /
CheXpert-style format after preprocessing — see dataset/README.md for how
to build this manifest from the raw datasets).
"""
import os
from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms

from model.labels import DISEASE_LABELS

IMAGE_SIZE = 224

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_transforms(train: bool = True) -> transforms.Compose:
    if train:
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ])
    return transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


class ChestXrayDataset(Dataset):
    """
    Args:
        manifest_csv: path to CSV with an `image_path` column plus one
            0/1 column per label in DISEASE_LABELS.
        image_root: directory to prefix relative image paths with.
        train: whether to apply training-time augmentation.
    """

    def __init__(self, manifest_csv: str, image_root: str = "", train: bool = True):
        # pandas is a training-only dependency (not installed in the lean
        # backend/worker runtime images) — imported lazily here so that
        # importing build_transforms() for inference doesn't require it.
        import pandas as pd

        self.df = pd.read_csv(manifest_csv)
        missing = [c for c in DISEASE_LABELS if c not in self.df.columns]
        if missing:
            raise ValueError(f"Manifest is missing label columns: {missing}")
        self.image_root = image_root
        self.transform = build_transforms(train)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        img_path = row["image_path"]
        if self.image_root:
            img_path = os.path.join(self.image_root, img_path)

        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)

        target = torch.tensor(row[DISEASE_LABELS].values.astype("float32"))
        return image, target
