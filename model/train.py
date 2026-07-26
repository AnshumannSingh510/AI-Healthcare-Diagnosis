"""
Training script for the chest X-ray multi-label classifier.

Usage:
    python train.py --train_csv data/train.csv --val_csv data/val.csv \
        --image_root data/images --epochs 30 --backbone densenet121

Saves the best checkpoint (by validation macro-AUROC) to model/weights/.
"""
import argparse
import os
import copy

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.metrics import roc_auc_score, f1_score
import numpy as np
from tqdm import tqdm

from model.dataset import ChestXrayDataset
from model.architecture import build_model
from model.labels import DISEASE_LABELS, NUM_CLASSES


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> dict:
    y_pred = (y_prob >= threshold).astype(int)

    per_class_auc = {}
    aucs = []
    for i, label in enumerate(DISEASE_LABELS):
        # AUROC undefined if a class has only one label value present in the batch/split
        if len(np.unique(y_true[:, i])) < 2:
            continue
        auc = roc_auc_score(y_true[:, i], y_prob[:, i])
        per_class_auc[label] = auc
        aucs.append(auc)

    macro_auc = float(np.mean(aucs)) if aucs else float("nan")
    accuracy = float((y_pred == y_true).mean())
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)

    return {
        "accuracy": accuracy,
        "macro_auroc": macro_auc,
        "per_class_auroc": per_class_auc,
        "macro_f1": float(macro_f1),
    }


def train_one_epoch(model, loader, optimizer, criterion, device) -> float:
    model.train()
    running_loss = 0.0
    for images, targets in tqdm(loader, desc="train", leave=False):
        images, targets = images.to(device), targets.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
    return running_loss / len(loader.dataset)


@torch.no_grad()
def evaluate(model, loader, criterion, device) -> tuple:
    model.eval()
    running_loss = 0.0
    all_targets, all_probs = [], []
    for images, targets in tqdm(loader, desc="val", leave=False):
        images, targets = images.to(device), targets.to(device)
        outputs = model(images)
        loss = criterion(outputs, targets)
        running_loss += loss.item() * images.size(0)
        probs = torch.sigmoid(outputs).cpu().numpy()
        all_probs.append(probs)
        all_targets.append(targets.cpu().numpy())

    y_prob = np.concatenate(all_probs)
    y_true = np.concatenate(all_targets)
    metrics = compute_metrics(y_true, y_prob)
    metrics["loss"] = running_loss / len(loader.dataset)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_csv", required=True)
    parser.add_argument("--val_csv", required=True)
    parser.add_argument("--image_root", default="")
    parser.add_argument("--backbone", default="densenet121", choices=["densenet121", "efficientnet_b0"])
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience (epochs)")
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--output_dir", default="model/weights")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_ds = ChestXrayDataset(args.train_csv, args.image_root, train=True)
    val_ds = ChestXrayDataset(args.val_csv, args.image_root, train=False)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

    model = build_model(args.backbone, pretrained=True, num_classes=NUM_CLASSES).to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)

    os.makedirs(args.output_dir, exist_ok=True)
    best_auroc = -1.0
    best_state = None
    epochs_without_improvement = 0

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_metrics = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_metrics["macro_auroc"])

        print(
            f"Epoch {epoch}/{args.epochs} | train_loss={train_loss:.4f} "
            f"| val_loss={val_metrics['loss']:.4f} | val_macro_auroc={val_metrics['macro_auroc']:.4f} "
            f"| val_macro_f1={val_metrics['macro_f1']:.4f} | val_acc={val_metrics['accuracy']:.4f}"
        )

        if val_metrics["macro_auroc"] > best_auroc:
            best_auroc = val_metrics["macro_auroc"]
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
            ckpt_path = os.path.join(args.output_dir, f"{args.backbone}_chest.pt")
            torch.save(
                {"model_state_dict": best_state, "backbone": args.backbone, "labels": DISEASE_LABELS},
                ckpt_path,
            )
            print(f"  -> New best model saved to {ckpt_path} (val_macro_auroc={best_auroc:.4f})")
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(f"Early stopping at epoch {epoch} (no improvement for {args.patience} epochs).")
                break

    print(f"Training complete. Best val_macro_auroc={best_auroc:.4f}")


if __name__ == "__main__":
    main()
