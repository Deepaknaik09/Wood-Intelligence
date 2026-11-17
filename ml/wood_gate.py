"""Wood / not-wood check (version 3: trained classifier).

Features: general ImageNet MobileNetV2 (independent of the species model).
Classifier: logistic regression trained on wood images (dataset + your photos
in extra_wood_samples/) versus non-wood images (non_wood_samples/).
The threshold is chosen from cross-validated scores on your own photos.

Build (several minutes):    python wood_gate.py build
Check images:               python wood_gate.py check <image_or_folder>
"""
import os
import sys
import random
import numpy as np

tf = None

def _ensure_tf():
    global tf
    if tf is None:
        import tensorflow as _tf
        tf = _tf

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE, "models")
GATE_PATH = os.path.join(MODELS_DIR, "wood_gate.npz")
DATA = os.path.join(BASE, "..", "datasets")
SPECIES_TRAIN = os.path.join(DATA, "wood_species", "Wood Dataset", "Train")
SPECIES_TEST = os.path.join(DATA, "wood_species", "Wood Dataset", "Test")
DEFECT_TRAIN = os.path.join(DATA, "wood_surface_defects", "yolo", "images", "train")
DEFECT_VAL = os.path.join(DATA, "wood_surface_defects", "yolo", "images", "val")
NON_WOOD_DIR = os.path.join(BASE, "non_wood_samples")
EXTRA_WOOD_DIR = os.path.join(BASE, "extra_wood_samples")
IMG_SIZE = (224, 224)
EXTS = (".jpg", ".jpeg", ".png")

_extractor = None
_gate = None


def get_extractor():
    """General ImageNet MobileNetV2 -> 1280 numbers per image."""
    global _extractor
    _ensure_tf()
    if _extractor is None:
        _extractor = tf.keras.applications.MobileNetV2(
            input_shape=IMG_SIZE + (3,), include_top=False,
            weights="imagenet", pooling="avg")
    return _extractor


def list_images(folder, recursive=False):
    paths = []
    if recursive:
        for dirpath, _, files in os.walk(folder):
            paths += [os.path.join(dirpath, f) for f in files
                      if f.lower().endswith(EXTS)]
    else:
        paths = [os.path.join(folder, f) for f in os.listdir(folder)
                 if f.lower().endswith(EXTS)]
    return sorted(paths)


def sample(paths, n, seed):
    rnd = random.Random(seed)
    paths = list(paths)
    rnd.shuffle(paths)
    return paths[:n]


def _load(path, augment=False):
    _ensure_tf()
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    if augment:
        h, w = int(img.shape[0]), int(img.shape[1])
        frac = random.uniform(0.35, 1.0)
        ch = min(h, max(32, int(h * frac)))
        cw = min(w, max(32, int(w * frac)))
        img = tf.image.random_crop(img, [ch, cw, 3])
    img = tf.image.resize(img, IMG_SIZE)
    img = tf.cast(img, tf.float32) / 255.0
    if augment:
        img = tf.image.random_hue(img, 0.08)
        img = tf.image.random_saturation(img, 0.5, 1.8)
        img = tf.image.random_brightness(img, 0.25)
        img = tf.image.random_contrast(img, 0.7, 1.4)
        img = tf.clip_by_value(img, 0.0, 1.0)
    return (img.numpy() * 2.0 - 1.0).astype("float32")


def embed_many(paths, augment=False, batch=32, quiet=False):
    """Unit-length embedding for each readable image (unreadable ones are skipped)."""
    out = []
    for i in range(0, len(paths), batch):
        arrs = []
        for p in paths[i:i + batch]:
            try:
                arrs.append(_load(p, augment))
            except Exception:
                continue
        if not arrs:
            continue
        feats = get_extractor().predict(np.stack(arrs), verbose=0)
        feats = feats / (np.linalg.norm(feats, axis=1, keepdims=True) + 1e-9)
        out.append(feats)
        if not quiet:
            print(f"  embedded {min(i + batch, len(paths))}/{len(paths)}", end="\r")
    if not quiet:
        print()
    if not out:
        return np.zeros((0, 1280), dtype="float32")
    return np.concatenate(out)


def wood_score(path):
    """Returns (probability of wood, threshold). Wood if score >= threshold."""
    global _gate
    if _gate is None:
        d = np.load(GATE_PATH)
        _gate = (d["coef"], float(d["intercept"]), float(d["threshold"]))
    coef, intercept, thr = _gate
    feat = embed_many([path], quiet=True)
    if feat.shape[0] == 0:
        return 0.0, thr
    z = float(np.clip(feat[0] @ coef + intercept, -30, 30))
    return float(1.0 / (1.0 + np.exp(-z))), thr


def make_clf():
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000)


def build():
    random.seed(0)
    np.random.seed(0)
    sp_train = sample(list_images(SPECIES_TRAIN, True), 1500, 1)
    df_train = sample(list_images(DEFECT_TRAIN), 1000, 1)
    held_paths = (sample(list_images(SPECIES_TEST), 300, 2)
                  + sample(list_images(DEFECT_VAL), 200, 2))
    wood_photos = list_images(EXTRA_WOOD_DIR) if os.path.isdir(EXTRA_WOOD_DIR) else []
    neg_photos = list_images(NON_WOOD_DIR) if os.path.isdir(NON_WOOD_DIR) else []
    if len(wood_photos) < 10 or len(neg_photos) < 10:
        print("WARNING: you need 20+ wood photos and 20+ non-wood photos "
              "for a reliable result.")

    X, Y, G, W = [], [], [], []

    def add(feats, label, group, weight):
        if feats.shape[0] == 0:
            return
        X.append(feats)
        Y.append(np.full(feats.shape[0], label))
        G.append(np.full(feats.shape[0], group))
        W.append(np.full(feats.shape[0], weight, dtype="float32"))

    print("Embedding dataset wood images:", len(sp_train) + len(df_train))
    add(embed_many(sp_train + df_train), 1, -1, 1.0)
    aug_paths = sample(sp_train, 400, 3) + sample(df_train, 300, 3)
    print("Embedding dataset colour/zoom variations:", len(aug_paths))
    add(embed_many(aug_paths, augment=True), 1, -1, 1.0)

    photos = [(p, 1) for p in wood_photos] + [(p, 0) for p in neg_photos]
    names, labels, orig_feats = [], [], []
    print("Embedding your wood and non-wood photos:", len(photos))
    for p, label in photos:
        orig = embed_many([p], quiet=True)
        if orig.shape[0] == 0:
            continue
        gid = len(names)
        variants = embed_many([p] * 12, augment=True, quiet=True)
        add(orig, label, gid, 3.0)
        add(variants, label, gid, 3.0)
        names.append(os.path.basename(p))
        labels.append(label)
        orig_feats.append(orig[0])

    X = np.concatenate(X)
    Y = np.concatenate(Y)
    G = np.concatenate(G)
    W = np.concatenate(W)
    labels = np.array(labels)
    orig_feats = np.array(orig_feats)
    n = len(names)

    print("Embedding held-out dataset wood images:", len(held_paths))
    held = embed_many(held_paths)

    print("Cross-validating on your photos (5 folds)...")
    ids = list(range(n))
    random.Random(5).shuffle(ids)
    oof = np.zeros(n)
    for k in range(5):
        fold = ids[k::5]
        train = ~np.isin(G, fold)
        clf = make_clf().fit(X[train], Y[train], sample_weight=W[train])
        oof[fold] = clf.predict_proba(orig_feats[fold])[:, 1]

    is_wood = labels == 1
    best, best_sum = [], -1.0
    for t in np.arange(0.05, 0.951, 0.01):
        tpr = float((oof[is_wood] >= t).mean()) if is_wood.any() else 0.0
        tnr = float((oof[~is_wood] < t).mean()) if (~is_wood).any() else 0.0
        if tpr + tnr > best_sum + 1e-9:
            best_sum, best = tpr + tnr, [t]
        elif abs(tpr + tnr - best_sum) <= 1e-9:
            best.append(t)
    threshold = float(np.clip(np.median(best), 0.10, 0.95))

    clf = make_clf().fit(X, Y, sample_weight=W)
    np.savez(GATE_PATH, coef=clf.coef_[0].astype("float32"),
             intercept=float(clf.intercept_[0]), threshold=threshold)
    held_prob = clf.predict_proba(held)[:, 1] if held.shape[0] else np.array([])

    wood_ok = int((oof[is_wood] >= threshold).sum())
    neg_ok = int((oof[~is_wood] < threshold).sum())
    print("\n=== RESULTS (each photo scored by a model that never saw it) ===")
    print(f"Threshold saved: {threshold:.2f}")
    print(f"Your wood photos accepted:      {wood_ok} of {int(is_wood.sum())}")
    print(f"Your non-wood photos rejected:  {neg_ok} of {int((~is_wood).sum())}")
    if held_prob.size:
        print(f"Held-out dataset wood accepted: "
              f"{int((held_prob >= threshold).sum())} of {held_prob.size}")
    print("\nWood score range:     lowest %.2f | median %.2f"
          % (oof[is_wood].min(), np.median(oof[is_wood])))
    print("Non-wood score range: highest %.2f | median %.2f"
          % (oof[~is_wood].max(), np.median(oof[~is_wood])))
    print("\nMistakes:")
    mistakes = 0
    for nm, lab, s in zip(names, labels, oof):
        if lab == 1 and s < threshold:
            print(f"  WOOD rejected:     {nm}  ({s:.2f})")
            mistakes += 1
        if lab == 0 and s >= threshold:
            print(f"  NON-WOOD accepted: {nm}  ({s:.2f})")
            mistakes += 1
    if mistakes == 0:
        print("  none")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "build":
        build()
    elif mode == "check" and len(sys.argv) > 2:
        target = sys.argv[2]
        paths = list_images(target) if os.path.isdir(target) else [target]
        for p in paths[:20]:
            s, thr = wood_score(p)
            label = "WOOD" if s >= thr else "NOT WOOD"
            print(f"{os.path.basename(p)}: score {s:.3f} (threshold {thr:.3f}) -> {label}")
    else:
        print("Usage: python wood_gate.py build | check <image_or_folder>")