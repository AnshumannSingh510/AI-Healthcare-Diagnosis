# Dataset Setup

This project trains on public chest X-ray datasets. It does **not** ship with
any patient data. Choose one of the following.

## Option A: NIH ChestX-ray14

1. Download from the NIH Clinical Center release:
   https://nihcc.app.box.com/v/ChestXray-NIHCC
   (or via Kaggle mirror: https://www.kaggle.com/datasets/nih-chest-xrays/data)
2. Extract images into `dataset/raw/nih/images/`.
3. The dataset ships with `Data_Entry_2017.csv` containing `Image Index` and
   `Finding Labels` (pipe-separated, e.g. `Cardiomegaly|Effusion`).
4. Run the conversion script to build a training manifest matching the label
   set in `model/labels.py`:

   ```bash
   python dataset/build_manifest.py \
     --source nih \
     --csv dataset/raw/nih/Data_Entry_2017.csv \
     --image_dir dataset/raw/nih/images \
     --output_train dataset/train.csv \
     --output_val dataset/val.csv
   ```

## Option B: CheXpert

1. Request access and download from Stanford ML Group:
   https://stanfordmlgroup.github.io/competitions/chexpert/
2. Extract into `dataset/raw/chexpert/`.
3. CheXpert ships `train.csv` / `valid.csv` with uncertainty-labeled columns
   (`-1`, `0`, `1`). Map `-1` (uncertain) to `0` or `1` per your chosen
   policy (the standard "U-Ones" or "U-Zeros" approach), then run:

   ```bash
   python dataset/build_manifest.py \
     --source chexpert \
     --csv dataset/raw/chexpert/train.csv \
     --image_dir dataset/raw/chexpert \
     --output_train dataset/train.csv \
     --output_val dataset/val.csv
   ```

## Manifest format

Both paths converge on a CSV with columns:

```
image_path,Normal,Pneumonia,Cardiomegaly,Fibrosis,Edema,Effusion,Atelectasis,Nodule,Mass,Pneumothorax
images/00000001_000.png,0,0,1,0,0,0,0,0,0,0
...
```

This is what `model/dataset.py`'s `ChestXrayDataset` expects. Once you have
`dataset/train.csv` and `dataset/val.csv`, train with:

```bash
python -m model.train \
  --train_csv dataset/train.csv \
  --val_csv dataset/val.csv \
  --image_root dataset/raw/nih \
  --epochs 30 \
  --backbone densenet121
```

The best checkpoint is written to `model/weights/densenet121_chest.pt`, which
is the path the backend/worker reads via `MODEL_WEIGHTS_PATH`.

## Skipping training

If you just want to run the full application stack without training your own
model, the inference pipeline (`model/predict.py`) will automatically fall
back to an ImageNet-pretrained DenseNet121 with an untrained classification
head — the app runs end-to-end, but predictions are not clinically
meaningful until a real checkpoint is trained and placed at
`model/weights/densenet121_chest.pt`.
