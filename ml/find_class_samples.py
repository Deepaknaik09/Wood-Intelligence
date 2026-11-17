"""
Phase 3 - Helper Script
Finds one sample image filename for each defect class ID (0-7),
so you can open and visually inspect them to confirm class names.

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python find_class_samples.py
"""

import os

LABELS_DIR = os.path.join(
    "..", "datasets", "wood_surface_defects",
    "Bounding Boxes - YOLO Format - 1", "Bounding Boxes - YOLO Format - 1"
)
IMAGES_DIR = os.path.join(
    "..", "datasets", "wood_surface_defects",
    "Images - 1", "Images - 1"
)

if __name__ == "__main__":
    found = {}
    for fname in sorted(os.listdir(LABELS_DIR)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(LABELS_DIR, fname)
        with open(path, "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        for line in lines:
            class_id = int(line.split()[0])
            if class_id not in found:
                img_name = fname.replace(".txt", ".jpg")
                img_path = os.path.join(IMAGES_DIR, img_name)
                if os.path.exists(img_path):
                    found[class_id] = img_path

    print("Sample image per class ID:")
    for class_id in sorted(found.keys()):
        print(f"  Class {class_id}: {found[class_id]}")
