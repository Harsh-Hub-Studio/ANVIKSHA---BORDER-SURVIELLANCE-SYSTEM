# ============================================================
# FILE: train_weapons.py
# PURPOSE: Train YOLOv8 on the weapon_detection dataset
#
# FIRST TIME SETUP:
#   pip install ultralytics
#
# RUN:
#   python train_weapons.py
#
# OUTPUT:
#   runs/detect/weapons/weights/best.pt  ← use this in your system
# ============================================================

from ultralytics import YOLO
import os

# ── CONFIG ───────────────────────────────────────────────────
DATASET_YAML = "weapon_detection/dataset.yaml"
BASE_MODEL   = "yolov8n.pt"
EPOCHS       = 50
IMG_SIZE     = 640
BATCH_SIZE   = 8
PROJECT_NAME = "runs/detect"
RUN_NAME     = "weapons"
LAST_WEIGHTS = os.path.join(PROJECT_NAME, RUN_NAME, "weights", "last.pt")

# ── AUTO-DETECT RESUME ────────────────────────────────────────
if os.path.exists(LAST_WEIGHTS):
    print("=" * 55)
    print("  ARGUS SENTINEL — Resuming Weapon Training")
    print(f"  Checkpoint : {LAST_WEIGHTS}")
    print("=" * 55)
    model   = YOLO(LAST_WEIGHTS)
    results = model.train(resume=True)
else:
    print("=" * 55)
    print("  ARGUS SENTINEL — Starting Weapon Training")
    print(f"  Dataset : {DATASET_YAML}")
    print(f"  Model   : {BASE_MODEL}")
    print(f"  Epochs  : {EPOCHS}")
    print(f"  Batch   : {BATCH_SIZE}")
    print("=" * 55)
    model   = YOLO(BASE_MODEL)
    results = model.train(
        data     = DATASET_YAML,
        epochs   = EPOCHS,
        imgsz    = IMG_SIZE,
        batch    = BATCH_SIZE,
        project  = PROJECT_NAME,
        name     = RUN_NAME,
        patience = 10,
        device   = "cpu",      # change to 0 if you have NVIDIA GPU
        workers  = 2,
        verbose  = True,
    )

print("\n" + "=" * 55)
print("  Training complete!")
print(f"  Best weights: {PROJECT_NAME}/{RUN_NAME}/weights/best.pt")
print("=" * 55)
