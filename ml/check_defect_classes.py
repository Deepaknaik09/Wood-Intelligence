"""
Phase 3 - Helper Script
Scans all YOLO label .txt files in the Wood Surface Defects dataset
to find which class IDs actually appear, and how often.

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python check_defect_classes.py
"""

import os
from collections import Counter

LABELS_DIR = os.path.join(
    "..", "datasets", "wood_surface_defects",
    "Bounding Boxes - YOLO Format - 1", "Bounding Boxes - YOLO Format - 1"
)

if __name__ == "__main__":
    class_counts = Counter()
    empty_files = 0
    total_files = 0
    total_boxes = 0

    for fname in os.listdir(LABELS_DIR):
        if not fname.endswith(".txt"):
            continue
        total_files += 1
        path = os.path.join(LABELS_DIR, fname)
        with open(path, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if not lines:
            empty_files += 1
            continue
        for line in lines:
            parts = line.split()
            if parts:
                class_id = int(parts[0])
                class_counts[class_id] += 1
                total_boxes += 1

    print("=" * 50)
    print("DEFECT LABEL CLASS SCAN")
    print("=" * 50)
    print(f"Total label files scanned: {total_files}")
    print(f"Empty label files (no defect): {empty_files}")
    print(f"Total bounding boxes found: {total_boxes}")
    print(f"Number of distinct class IDs: {len(class_counts)}")
    print("\nClass ID : Count")
    for class_id in sorted(class_counts.keys()):
        print(f"  {class_id:>3} : {class_counts[class_id]}")
