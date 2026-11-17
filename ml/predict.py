"""Phase 6 - Inference pipeline: wood species + surface defect detection.

Usage (from the ml folder, venv active):
    python predict.py <image_or_folder>
A folder runs on its first 3 images.
Annotated images and results.json are saved to ml/outputs/.
"""
import os
import sys
import json

# ── Import order matters ────────────────────────────────────────────────────
# torch + torchvision.ops MUST be imported before tensorflow and ultralytics.
# Reason: torchvision/_meta_registrations.py registers the C-level NMS kernel
# via torch.library.register_fake('torchvision::nms').  If tensorflow is
# imported first it patches torch internals in a way that the kernel
# registration raises "operator torchvision::nms does not exist".
# Pre-loading torchvision.ops forces the C extension (_C.pyd) to load and
# register its kernels before any framework can interfere.
import numpy as np
import cv2

# Lazy-loaded backend to achieve instantaneous application startup
tf = None
YOLO = None

def _ensure_backend():
    global tf, YOLO
    if tf is None:
        import torch                    # noqa: F401 — must precede torchvision
        import torchvision.ops          # noqa: F401 — registers NMS C kernel early
        import tensorflow as _tf
        tf = _tf
    if YOLO is None:
        from ultralytics import YOLO as _YOLO
        YOLO = _YOLO

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE, "models")
SPECIES_MODEL_PATH = os.path.join(MODELS_DIR, "wood_species_model_ext.h5")   # 19-class model
LABELS_PATH = os.path.join(MODELS_DIR, "labels_ext.json")
DEFECT_MODEL_PATH = os.path.join(MODELS_DIR, "defect_runs", "v1", "weights", "best.pt")
OUTPUT_DIR = os.path.join(BASE, "outputs")

IMG_SIZE = (224, 224)      # species model input
DEFECT_IMGSZ = 416         # defect model input
DEFECT_CONF = 0.35         # minimum confidence to report a defect

# Fill these in once you know the real names, e.g. {"1": "Teak"} and {0: "Knot"}
SPECIES_NAMES = {'1': 'European beech (Fagus sylvatica)', '2': 'Walnut (Juglans regia)', '3': 'Sweet chestnut (Castanea sativa)', '4': 'Turkey oak (Quercus cerris)', '5': 'Black alder (Alnus glutinosa)', '6': 'Manna ash (Fraxinus ornus)', '7': 'Norway spruce (Picea abies)', '8': 'Scots pine (Pinus sylvestris)', '9': 'Tree of heaven (Ailanthus altissima)', '10': 'Black locust (Robinia pseudoacacia)', '11': 'Mediterranean cypress (Cupressus sempervirens)', '12': 'Oriental plane (Platanus orientalis)', '13': 'Akashmoni', '14': 'Eucalyptus', '15': 'Kathal (Jackfruit)', '16': 'Loha', '17': 'Mahogany', '18': 'Minjiri', '19': 'Rain tree'}
DEFECT_NAMES = {0: 'Quartzity', 1: 'Live knot', 2: 'Marrow', 3: 'Resin', 4: 'Dead knot', 5: 'Knot with crack', 6: 'Knot missing', 7: 'Crack'}

IMAGE_EXTS = (".jpg", ".jpeg", ".png")

_species_model = None
_species_labels = None
_defect_model = None


def load_models():
    global _species_model, _species_labels, _defect_model
    _ensure_backend()
    if _species_model is None:
        _species_model = tf.keras.models.load_model(SPECIES_MODEL_PATH, compile=False)
        with open(LABELS_PATH) as f:
            raw = json.load(f)
        _species_labels = {int(k): v for k, v in raw.items()}
    if _defect_model is None:
        _defect_model = YOLO(DEFECT_MODEL_PATH)


def species_display(folder_id):
    return SPECIES_NAMES.get(folder_id, f"Species {folder_id}")


def defect_display(class_id):
    return DEFECT_NAMES.get(class_id, f"defect_{class_id}")


def predict_species(image_path, top_k=3, patches=True):
    """Average the species model's answer over the whole image and 9 overlapping
    patches, so fine-grained grain texture isn't lost when a large photo is
    squashed down to 224x224."""
    load_models()
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    h, w = int(img.shape[0]), int(img.shape[1])

    views = [tf.image.resize(img, IMG_SIZE)]
    side = int(min(h, w) * 0.5)
    if patches and side >= 32:
        for y in np.linspace(0, h - side, 3).astype(int):
            for x in np.linspace(0, w - side, 3).astype(int):
                views.append(tf.image.resize(img[y:y + side, x:x + side, :], IMG_SIZE))

    batch = tf.stack(views) / 255.0
    probs = _species_model.predict(batch, verbose=0).mean(axis=0)
    order = np.argsort(probs)[::-1][:top_k]
    top = [{
        "folder_id": _species_labels[int(i)],
        "name": species_display(_species_labels[int(i)]),
        "confidence": round(float(probs[i]), 4),
    } for i in order]
    return top


def predict_defects(image_path):
    load_models()
    result = _defect_model.predict(
        source=image_path, imgsz=DEFECT_IMGSZ, conf=DEFECT_CONF,
        iou=0.5, agnostic_nms=True,
        device="cpu", verbose=False)[0]
    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        x1, y1, x2, y2 = [round(float(v), 1) for v in box.xyxy[0]]
        detections.append({
            "class_id": class_id,
            "name": defect_display(class_id),
            "confidence": round(float(box.conf[0]), 4),
            "box_xyxy": [x1, y1, x2, y2],
        })
    detections.sort(key=lambda d: d["confidence"], reverse=True)
    annotated = result.plot()   # BGR image with boxes drawn
    return detections, annotated


def analyze(image_path, save_annotated=True):
    """Run both models on one image and return a results dict."""
    load_models()
    species_top = predict_species(image_path)
    detections, annotated = predict_defects(image_path)

    annotated_path = None
    if save_annotated:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        stem = os.path.splitext(os.path.basename(image_path))[0]
        annotated_path = os.path.join(OUTPUT_DIR, f"{stem}_annotated.jpg")
        cv2.imwrite(annotated_path, annotated)

    return {
        "image": os.path.abspath(image_path),
        "species": species_top[0],
        "species_top3": species_top,
        "defect_count": len(detections),
        "defects": detections,
        "annotated_image": annotated_path,
    }


def list_images(path):
    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.lower().endswith(IMAGE_EXTS))
        return [os.path.join(path, f) for f in files[:3]]
    return [path]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_or_folder>")
        sys.exit(1)

    images = list_images(sys.argv[1])
    if not images:
        print("No images found.")
        sys.exit(1)

    all_results = []
    for p in images:
        r = analyze(p)
        all_results.append(r)
        print("\n" + "=" * 60)
        print("Image:", os.path.basename(p))
        s = r["species"]
        print(f"Species: {s['name']}  (confidence {s['confidence'] * 100:.1f}%)")
        print("  Top 3:", ", ".join(
            f"{t['name']} {t['confidence'] * 100:.0f}%" for t in r["species_top3"]))
        print(f"Defects found: {r['defect_count']}")
        for d in r["defects"]:
            print(f"  - {d['name']}  {d['confidence'] * 100:.0f}%  box={d['box_xyxy']}")
        print("Annotated image:", r["annotated_image"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_json = os.path.join(OUTPUT_DIR, "results.json")
    with open(out_json, "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved results to:", out_json)