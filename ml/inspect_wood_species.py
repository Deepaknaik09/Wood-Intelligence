"""
Phase 2 - Dataset Inspection Script (v2)
Wood Species Dataset (Zenodo 2545611)

Train/ is organized into class subfolders (1-12).
Test/ is a FLAT folder where each filename ends in _<class>.jpg
  e.g. "100_1.jpg" -> class 1, "497_12.jpg" -> class 12

This script counts images per class for both splits correctly,
and displays a sample image grid.

Run this from inside the ml/ folder of your project:
    cd D:\Main_Project\wood-intelligence-project\ml
    python inspect_wood_species.py
"""

import os
import re
from collections import Counter
import matplotlib.pyplot as plt
from PIL import Image

# ---- CONFIG ----
DATASET_ROOT = os.path.join("..", "datasets", "wood_species", "Wood Dataset")
TRAIN_DIR = os.path.join(DATASET_ROOT, "Train")
TEST_DIR = os.path.join(DATASET_ROOT, "Test")


def count_train(split_dir):
    """Train/ has one subfolder per class."""
    print(f"\n--- Train ---")
    counts = {}
    class_folders = sorted(
        [f for f in os.listdir(split_dir) if os.path.isdir(os.path.join(split_dir, f))],
        key=lambda x: int(x) if x.isdigit() else x
    )
    for class_name in class_folders:
        class_path = os.path.join(split_dir, class_name)
        num_images = len([
            f for f in os.listdir(class_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])
        counts[class_name] = num_images
        print(f"  Class {class_name:>3}: {num_images} images")
    total = sum(counts.values())
    print(f"  TOTAL Train: {total} images across {len(counts)} classes")
    return counts


def count_test(split_dir):
    """Test/ is flat; class is the number after the underscore in the filename."""
    print(f"\n--- Test ---")
    pattern = re.compile(r"_(\d+)\.(jpg|jpeg|png)$", re.IGNORECASE)
    counts = Counter()
    for fname in os.listdir(split_dir):
        match = pattern.search(fname)
        if match:
            class_name = match.group(1)
            counts[class_name] += 1

    for class_name in sorted(counts.keys(), key=lambda x: int(x)):
        print(f"  Class {class_name:>3}: {counts[class_name]} images")
    total = sum(counts.values())
    print(f"  TOTAL Test: {total} images across {len(counts)} classes")
    return dict(counts)


def show_sample_grid(train_dir, test_dir, class_list):
    """Display one sample image from each class (pulled from Train)."""
    n_classes = len(class_list)
    cols = 4
    rows = (n_classes + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
    axes = axes.flatten()

    for idx, class_name in enumerate(class_list):
        class_path = os.path.join(train_dir, class_name)
        images = [
            f for f in os.listdir(class_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if images:
            img_path = os.path.join(class_path, images[0])
            img = Image.open(img_path)
            axes[idx].imshow(img)
            axes[idx].set_title(f"Class {class_name}")
        axes[idx].axis("off")

    for idx in range(n_classes, len(axes)):
        axes[idx].axis("off")

    plt.tight_layout()
    output_path = "wood_species_sample_grid.png"
    plt.savefig(output_path, dpi=150)
    print(f"\nSample grid saved to: {os.path.abspath(output_path)}")
    plt.show()


if __name__ == "__main__":
    print("=" * 50)
    print("WOOD SPECIES DATASET INSPECTION (v2)")
    print("=" * 50)

    train_counts = count_train(TRAIN_DIR)
    test_counts = count_test(TEST_DIR)

    grand_total = sum(train_counts.values()) + sum(test_counts.values())
    print(f"\nGRAND TOTAL (Train + Test): {grand_total} images")
    print(f"Expected from Zenodo listing: 8544 images")
    print(f"Number of species classes: {len(train_counts)}")

    print("\n--- Combined per-class summary ---")
    for class_name in sorted(train_counts.keys(), key=lambda x: int(x)):
        tr = train_counts.get(class_name, 0)
        te = test_counts.get(class_name, 0)
        print(f"  Class {class_name:>3}: Train={tr:>4}  Test={te:>4}  Total={tr+te:>4}")

    class_list = sorted(train_counts.keys(), key=lambda x: int(x))
    show_sample_grid(TRAIN_DIR, TEST_DIR, class_list)
