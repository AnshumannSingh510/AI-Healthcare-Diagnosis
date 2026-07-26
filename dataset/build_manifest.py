"""
Converts raw NIH ChestX-ray14 or CheXpert label CSVs into the manifest
format expected by model/dataset.py's ChestXrayDataset:

    image_path,Normal,Pneumonia,Cardiomegaly,Fibrosis,Edema,Effusion,
    Atelectasis,Nodule,Mass,Pneumothorax

Usage:
    python dataset/build_manifest.py --source nih \
        --csv dataset/raw/nih/Data_Entry_2017.csv \
        --image_dir dataset/raw/nih/images \
        --output_train dataset/train.csv --output_val dataset/val.csv

    python dataset/build_manifest.py --source chexpert \
        --csv dataset/raw/chexpert/train.csv \
        --image_dir dataset/raw/chexpert \
        --output_train dataset/train.csv --output_val dataset/val.csv
"""
import argparse
import os
import sys

import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.labels import DISEASE_LABELS  # noqa: E402

# Maps each dataset's native label spelling -> our canonical label set.
# Any native label not present here is ignored (out of scope for this app).
NIH_LABEL_MAP = {
    "No Finding": "Normal",
    "Pneumonia": "Pneumonia",
    "Cardiomegaly": "Cardiomegaly",
    "Fibrosis": "Fibrosis",
    "Edema": "Edema",
    "Effusion": "Effusion",
    "Atelectasis": "Atelectasis",
    "Nodule": "Nodule",
    "Mass": "Mass",
    "Pneumothorax": "Pneumothorax",
}

CHEXPERT_LABEL_MAP = {
    "No Finding": "Normal",
    "Pneumonia": "Pneumonia",
    "Cardiomegaly": "Cardiomegaly",
    "Edema": "Edema",
    "Pleural Effusion": "Effusion",
    "Atelectasis": "Atelectasis",
    # CheXpert doesn't natively include Fibrosis/Nodule/Mass/Pneumothorax
    # under identical names for all versions; extend this map if your
    # CheXpert CSV version includes them.
}


def build_from_nih(csv_path: str, image_dir: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    rows = []
    skipped = 0
    for _, r in df.iterrows():
        image_path = os.path.join(image_dir, r["Image Index"])
        if not os.path.exists(image_path):
            skipped += 1
            continue
        labels = set(r["Finding Labels"].split("|"))
        row = {"image_path": image_path}
        for canonical in DISEASE_LABELS:
            native_names = [k for k, v in NIH_LABEL_MAP.items() if v == canonical]
            row[canonical] = int(any(n in labels for n in native_names))
        rows.append(row)
    if skipped:
        print(f"Skipped {skipped} rows from the CSV whose image file was not found in {image_dir} "
              f"(expected if you downloaded a partial/sample dataset).")
    return pd.DataFrame(rows)


def build_from_chexpert(csv_path: str, image_dir: str, uncertainty_policy: str = "zeros") -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    rows = []
    skipped = 0
    for _, r in df.iterrows():
        image_path = os.path.join(image_dir, r["Path"])
        if not os.path.exists(image_path):
            skipped += 1
            continue
        row = {"image_path": image_path}
        for canonical in DISEASE_LABELS:
            native_names = [k for k, v in CHEXPERT_LABEL_MAP.items() if v == canonical]
            val = 0
            for n in native_names:
                if n in r and pd.notna(r[n]):
                    raw = float(r[n])
                    if raw == 1.0:
                        val = 1
                    elif raw == -1.0:  # uncertain
                        val = 1 if uncertainty_policy == "ones" else 0
            row[canonical] = val
        rows.append(row)
    if skipped:
        print(f"Skipped {skipped} rows from the CSV whose image file was not found in {image_dir} "
              f"(expected if you downloaded a partial/sample dataset).")
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["nih", "chexpert"], required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--image_dir", required=True)
    parser.add_argument("--output_train", required=True)
    parser.add_argument("--output_val", required=True)
    parser.add_argument("--val_size", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.source == "nih":
        manifest = build_from_nih(args.csv, args.image_dir)
    else:
        manifest = build_from_chexpert(args.csv, args.image_dir)

    if len(manifest) == 0:
        raise SystemExit(
            f"No matching images found under --image_dir '{args.image_dir}'. "
            "Check that this path points to the folder containing the actual "
            ".png/.jpg files referenced by the CSV."
        )

    train_df, val_df = train_test_split(manifest, test_size=args.val_size, random_state=args.seed)
    os.makedirs(os.path.dirname(args.output_train) or ".", exist_ok=True)
    train_df.to_csv(args.output_train, index=False)
    val_df.to_csv(args.output_val, index=False)
    print(f"Wrote {len(train_df)} training rows to {args.output_train}")
    print(f"Wrote {len(val_df)} validation rows to {args.output_val}")


if __name__ == "__main__":
    main()
