"""
Phase 3 - Helper Script
Draws YOLO bounding boxes (with class ID labels) on one sample image
per defect class, and saves annotated versions to inspect visually.

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python visualize_defect_samples.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

LABELS_DIR = os.path.join(
    "..", "datasets", "wood_surface_defects",
    "Bounding Boxes - YOLO Format - 1", "Bounding Boxes - YOLO Format - 1"
)
IMAGES_DIR = os.path.join(
    "..", "datasets", "wood_surface_defects",
    "Images - 1", "Images - 1"
)
OUTPUT_DIR = "defect_class_samples"

COLORS = {
    0: "red", 1: "lime", 2: "blue", 3: "yellow",
    4: "magenta", 5: "cyan", 6: "orange", 7: "white"
}


def draw_boxes(image_path, label_path, out_path):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    with open(label_path, "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    for line in lines:
        parts = line.split()
        class_id = int(parts[0])
        xc, yc, bw, bh = map(float, parts[1:5])
        x1 = (xc - bw / 2) * w
        y1 = (yc - bh / 2) * h
        x2 = (xc + bw / 2) * w
        y2 = (yc + bh / 2) * h
        color = COLORS.get(class_id, "red")
        draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
        draw.text((x1 + 4, y1 + 4), f"class {class_id}", fill=color)

    img.save(out_path)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find one sample image per class
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
                    found[class_id] = (img_path, path)

    for class_id, (img_path, label_path) in sorted(found.items()):
        out_path = os.path.join(OUTPUT_DIR, f"class_{class_id}_annotated.jpg")
        draw_boxes(img_path, label_path, out_path)
        print(f"Saved: {out_path}")

    print(f"\nAll annotated samples saved in: {os.path.abspath(OUTPUT_DIR)}")
