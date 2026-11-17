"""
Phase 3 - Preprocessing Script
Wood Surface Defects Dataset (YOLO format)

Splits the 4,000 images + labels into an 80/20 train/val split,
organized into the folder structure Ultralytics YOLO expects:

    wood_surface_defects/
        images/train/
        images/val/
        labels/train/
        labels/val/

Also generates a data.yaml config file for training.

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python split_defects_dataset.py
"""

import os
import random
import shutil

# ---- CONFIG ----
RANDOM_SEED = 42
VAL_SPLIT = 0.2

DATASET_ROOT = os.path.join("..", "datasets", "wood_surface_defects")
IMAGES_SRC = os.path.join(DATASET_ROOT, "Images - 1", "Images - 1")
LABELS_SRC = os.path.join(DATASET_ROOT, "Bounding Boxes - YOLO Format - 1",
                          "Bounding Boxes - YOLO Format - 1")

IMAGES_TRAIN = os.path.join(DATASET_ROOT, "images", "train")
IMAGES_VAL = os.path.join(DATASET_ROOT, "images", "val")
LABELS_TRAIN = os.path.join(DATASET_ROOT, "labels", "train")
LABELS_VAL = os.path.join(DATASET_ROOT, "labels", "val")

NUM_CLASSES = 8
# Generic class names since no official mapping file was provided with this subset.
# Rename these later if you find better documentation for the exact defect types.
CLASS_NAMES = [f"defect_{i}" for i in range(NUM_CLASSES)]


def make_dirs():
    for d in [IMAGES_TRAIN, IMAGES_VAL, LABELS_TRAIN, LABELS_VAL]:
        os.makedirs(d, exist_ok=True)


def get_matched_pairs():
    """Match each image to its label file by filename stem."""
    image_files = sorted([f for f in os.listdir(IMAGES_SRC) if f.lower().endswith(".jpg")])
    pairs = []
    for img_name in image_files:
        stem = os.path.splitext(img_name)[0]
        label_name = stem + ".txt"
        label_path = os.path.join(LABELS_SRC, label_name)
        if os.path.exists(label_path):
            pairs.append((img_name, label_name))
    return pairs


def split_and_copy(pairs):
    random.seed(RANDOM_SEED)
    random.shuffle(pairs)

    val_count = int(len(pairs) * VAL_SPLIT)
    val_pairs = pairs[:val_count]
    train_pairs = pairs[val_count:]

    for img_name, label_name in train_pairs:
        shutil.copy(os.path.join(IMAGES_SRC, img_name), os.path.join(IMAGES_TRAIN, img_name))
        shutil.copy(os.path.join(LABELS_SRC, label_name), os.path.join(LABELS_TRAIN, label_name))

    for img_name, label_name in val_pairs:
        shutil.copy(os.path.join(IMAGES_SRC, img_name), os.path.join(IMAGES_VAL, img_name))
        shutil.copy(os.path.join(LABELS_SRC, label_name), os.path.join(LABELS_VAL, label_name))

    return len(train_pairs), len(val_pairs)


def write_data_yaml():
    yaml_path = os.path.join(DATASET_ROOT, "data.yaml")
    train_abs = os.path.abspath(IMAGES_TRAIN).replace("\\", "/")
    val_abs = os.path.abspath(IMAGES_VAL).replace("\\", "/")

    with open(yaml_path, "w") as f:
        f.write(f"train: {train_abs}\n")
        f.write(f"val: {val_abs}\n")
        f.write(f"nc: {NUM_CLASSES}\n")
        f.write(f"names: {CLASS_NAMES}\n")

    return yaml_path


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 3 - WOOD SURFACE DEFECTS: TRAIN/VAL SPLIT")
    print("=" * 60)

    print("\nCreating folder structure...")
    make_dirs()

    print("Matching images to labels...")
    pairs = get_matched_pairs()
    print(f"Total matched image-label pairs: {len(pairs)}")

    print(f"\nSplitting {int((1-VAL_SPLIT)*100)}% train / {int(VAL_SPLIT*100)}% val and copying files...")
    train_count, val_count = split_and_copy(pairs)
    print(f"  Train: {train_count} images")
    print(f"  Val:   {val_count} images")

    print("\nWriting data.yaml...")
    yaml_path = write_data_yaml()
    print(f"  Saved to: {os.path.abspath(yaml_path)}")

    print("\nPhase 3 (defects dataset) preprocessing complete.")
    print("Folder structure ready for YOLOv8 training in Phase 5.")
