"""Re-split the defect dataset 70/15/15 (train/val/test) into datasets/wood_surface_defects/yolo/
Leaves the earlier images/ and labels/ split untouched."""
import os
import random
import shutil
from collections import Counter

SEED = 42
ROOT = os.path.join("..", "datasets", "wood_surface_defects")
IMAGES_SRC = os.path.join(ROOT, "Images - 1", "Images - 1")
LABELS_SRC = os.path.join(ROOT, "Bounding Boxes - YOLO Format - 1",
                          "Bounding Boxes - YOLO Format - 1")
OUT = os.path.join(ROOT, "yolo")
NUM_CLASSES = 8
CLASS_NAMES = [f"defect_{i}" for i in range(NUM_CLASSES)]

if os.path.exists(OUT):
    shutil.rmtree(OUT)

pairs = []
for img in sorted(os.listdir(IMAGES_SRC)):
    if img.lower().endswith(".jpg"):
        stem = os.path.splitext(img)[0]
        lbl = stem + ".txt"
        if os.path.exists(os.path.join(LABELS_SRC, lbl)):
            pairs.append((img, lbl))
print("Matched pairs:", len(pairs))

random.seed(SEED)
random.shuffle(pairs)
n = len(pairs)
n_val = int(n * 0.15)
n_test = int(n * 0.15)
splits = {
    "test": pairs[:n_test],
    "val": pairs[n_test:n_test + n_val],
    "train": pairs[n_test + n_val:],
}

for split, items in splits.items():
    os.makedirs(os.path.join(OUT, "images", split), exist_ok=True)
    os.makedirs(os.path.join(OUT, "labels", split), exist_ok=True)
    counts = Counter()
    for img, lbl in items:
        shutil.copy(os.path.join(IMAGES_SRC, img), os.path.join(OUT, "images", split, img))
        shutil.copy(os.path.join(LABELS_SRC, lbl), os.path.join(OUT, "labels", split, lbl))
        with open(os.path.join(LABELS_SRC, lbl)) as f:
            for line in f:
                if line.strip():
                    counts[int(line.split()[0])] += 1
    print(f"\n{split}: {len(items)} images")
    print("  boxes per class:", {c: counts[c] for c in range(NUM_CLASSES)})

yaml_path = os.path.join(OUT, "data.yaml")
base = os.path.abspath(OUT).replace("\\", "/")
with open(yaml_path, "w") as f:
    f.write(f"path: {base}\n")
    f.write("train: images/train\n")
    f.write("val: images/val\n")
    f.write("test: images/test\n")
    f.write(f"nc: {NUM_CLASSES}\n")
    f.write(f"names: {CLASS_NAMES}\n")
print("\nSaved:", os.path.abspath(yaml_path))