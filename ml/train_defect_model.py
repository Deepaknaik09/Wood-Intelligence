"""Phase 5 - Train a YOLO defect detector on the wood surface defects dataset.
Run:  python train_defect_model.py
If a run is interrupted, set RESUME = True and run it again."""
import os
from ultralytics import YOLO

# ---- SETTINGS ----
MODEL = "yolo11n.pt"
EPOCHS = 30
IMGSZ = 416
FRACTION = 1.0            # 1.0 = all training images
BATCH = 16
PATIENCE = 8              # stop early if val mAP stops improving
RUN_NAME = "v1"
RESUME = False            # True = continue an interrupted run

DATA = os.path.abspath(os.path.join(
    "..", "datasets", "wood_surface_defects", "yolo", "data.yaml"))
PROJECT = os.path.abspath(os.path.join("models", "defect_runs"))

if __name__ == "__main__":
    if RESUME:
        last = os.path.join(PROJECT, RUN_NAME, "weights", "last.pt")
        model = YOLO(last)
        model.train(resume=True)
    else:
        model = YOLO(MODEL)
        model.train(
            data=DATA, epochs=EPOCHS, imgsz=IMGSZ, fraction=FRACTION,
            batch=BATCH, patience=PATIENCE, device="cpu", workers=2,
            project=PROJECT, name=RUN_NAME, exist_ok=True,
        )

    best = os.path.join(PROJECT, RUN_NAME, "weights", "best.pt")
    print("\nBest weights:", best)

    print("\nEvaluating on the TEST split...")
    metrics = YOLO(best).val(data=DATA, split="test", imgsz=IMGSZ,
                             device="cpu", workers=2)
    names = metrics.names
    print(f"\nTest mAP50:    {metrics.box.map50:.3f}")
    print(f"Test mAP50-95: {metrics.box.map:.3f}")
    print("Per-class mAP50:")
    for i, c in enumerate(metrics.box.ap_class_index):
        print(f"  {names[int(c)]}: {metrics.box.ap50[i]:.3f}")