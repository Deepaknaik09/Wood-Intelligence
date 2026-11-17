"""Make a contact sheet of labelled examples for each defect class.
Run from the ml folder:  python make_class_sheets.py
Output: ml/defect_class_sheets/class_N_sheet.jpg"""
import os
import random
import cv2
import numpy as np

ROOT = os.path.join("..", "datasets", "wood_surface_defects", "yolo")
IMG_DIR = os.path.join(ROOT, "images", "train")
LBL_DIR = os.path.join(ROOT, "labels", "train")
OUT = "defect_class_sheets"
CELL, COLS, ROWS = 240, 4, 2
N = COLS * ROWS
random.seed(1)
os.makedirs(OUT, exist_ok=True)

boxes = {c: [] for c in range(8)}
for name in os.listdir(LBL_DIR):
    if not name.endswith(".txt"):
        continue
    with open(os.path.join(LBL_DIR, name)) as f:
        for line in f:
            p = line.split()
            if len(p) == 5:
                boxes[int(p[0])].append((name[:-4],) + tuple(map(float, p[1:])))

for c in range(8):
    items = boxes[c]
    random.shuffle(items)
    cells = []
    for stem, cx, cy, w, h in items:
        if len(cells) >= N:
            break
        img = cv2.imread(os.path.join(IMG_DIR, stem + ".jpg"))
        if img is None:
            continue
        H, W = img.shape[:2]
        bw, bh = w * W, h * H
        pad = max(20, 0.3 * max(bw, bh))
        x1 = int(max(0, cx * W - bw / 2 - pad))
        x2 = int(min(W, cx * W + bw / 2 + pad))
        y1 = int(max(0, cy * H - bh / 2 - pad))
        y2 = int(min(H, cy * H + bh / 2 + pad))
        crop = img[y1:y2, x1:x2].copy()
        scale = min(CELL / crop.shape[1], CELL / crop.shape[0])
        thick = max(2, int(2 / scale))
        bx1 = int(cx * W - bw / 2) - x1
        by1 = int(cy * H - bh / 2) - y1
        bx2 = int(cx * W + bw / 2) - x1
        by2 = int(cy * H + bh / 2) - y1
        cv2.rectangle(crop, (bx1, by1), (bx2, by2), (0, 255, 0), thick)
        crop = cv2.resize(crop, (max(1, int(crop.shape[1] * scale)),
                                 max(1, int(crop.shape[0] * scale))))
        cell = np.zeros((CELL, CELL, 3), np.uint8)
        oy = (CELL - crop.shape[0]) // 2
        ox = (CELL - crop.shape[1]) // 2
        cell[oy:oy + crop.shape[0], ox:ox + crop.shape[1]] = crop
        cells.append(cell)
    while len(cells) < N:
        cells.append(np.zeros((CELL, CELL, 3), np.uint8))
    rows = [np.hstack(cells[r * COLS:(r + 1) * COLS]) for r in range(ROWS)]
    sheet = np.vstack(rows)
    cv2.putText(sheet, f"class {c}  ({len(boxes[c])} boxes in train)", (10, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    out = os.path.join(OUT, f"class_{c}_sheet.jpg")
    cv2.imwrite(out, sheet)
    print("Saved", out)