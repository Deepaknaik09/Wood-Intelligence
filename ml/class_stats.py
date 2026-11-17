"""Box size statistics per defect class, from your own label files.
Run from the ml folder:  python class_stats.py"""
import os
import statistics as st

W_PX, H_PX = 2800, 1024
boxes = {c: [] for c in range(8)}
for split in ("train", "val", "test"):
    d = os.path.join("..", "datasets", "wood_surface_defects", "yolo", "labels", split)
    for name in os.listdir(d):
        if not name.endswith(".txt"):
            continue
        with open(os.path.join(d, name)) as f:
            for line in f:
                p = line.split()
                if len(p) == 5:
                    boxes[int(p[0])].append((float(p[3]) * W_PX, float(p[4]) * H_PX))

print("class  count  median_w_px  median_h_px  tall(h>400px)  squarish  wide(w>220px)")
for c in range(8):
    b = boxes[c]
    if not b:
        continue
    mw = st.median(w for w, h in b)
    mh = st.median(h for w, h in b)
    tall = sum(h > 400 for w, h in b) / len(b)
    sq = sum(0.7 <= h / max(w, 1) <= 1.4 for w, h in b) / len(b)
    wide = sum(w > 220 for w, h in b) / len(b)
    print(f"{c:>5} {len(b):>6} {mw:>12.0f} {mh:>12.0f} {tall:>13.0%} {sq:>9.0%} {wide:>13.0%}")