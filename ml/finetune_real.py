"""Phase 6b - Fine-tune the species model on real-world photos.

Folder layout (inside ml/):
    real_photos/1/  ... real_photos/12/     <- folder id = dataset class id
Run from the ml folder with the venv active:
    python finetune_real.py
Saves models/wood_species_model_real.h5 (old model is NOT touched).
"""
import os
import re
import json
import random
import numpy as np
import tensorflow as tf

BASE = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE, "models")
SRC_MODEL = os.path.join(MODELS_DIR, "wood_species_model_ft.h5")
OUT_MODEL = os.path.join(MODELS_DIR, "wood_species_model_real.h5")
LABELS_PATH = os.path.join(MODELS_DIR, "labels.json")
REAL_DIR = os.path.join(BASE, "real_photos")
DATASET_ROOT = os.path.join(BASE, "..", "datasets", "wood_species", "Wood Dataset")
TRAIN_DIR = os.path.join(DATASET_ROOT, "Train")
TEST_DIR = os.path.join(DATASET_ROOT, "Test")

IMG = (224, 224)
BATCH = 32
EPOCHS = 15
LR = 2e-5
REAL_REPEAT = 8
ORIG_PER_CLASS = 80
TEST_SAMPLE = 600
VAL_FRACTION = 0.2
SEED = 42
EXTS = (".jpg", ".jpeg", ".png")
AUTOTUNE = tf.data.AUTOTUNE

random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

with open(LABELS_PATH) as f:
    _raw = json.load(f)
FOLDER_TO_IDX = {v: int(k) for k, v in _raw.items()}


def list_images(folder):
    return sorted(os.path.join(folder, f) for f in os.listdir(folder)
                  if f.lower().endswith(EXTS))


def collect_real():
    train, val = [], []
    print("Real photos per class (train / held-out):")
    for folder_id, idx in sorted(FOLDER_TO_IDX.items(), key=lambda kv: int(kv[0])):
        d = os.path.join(REAL_DIR, folder_id)
        files = list_images(d) if os.path.isdir(d) else []
        random.shuffle(files)
        n_val = max(1, round(len(files) * VAL_FRACTION)) if len(files) >= 5 else 0
        val += [(p, idx) for p in files[:n_val]]
        train += [(p, idx) for p in files[n_val:]]
        flag = "   <-- too few, add more!" if len(files) < 8 else ""
        print(f"  class {folder_id:>2}: {len(files) - n_val:>3} / {n_val}{flag}")
    return train, val


def collect_original():
    items = []
    for folder_id, idx in FOLDER_TO_IDX.items():
        d = os.path.join(TRAIN_DIR, folder_id)
        files = list_images(d)
        random.shuffle(files)
        items += [(p, idx) for p in files[:ORIG_PER_CLASS]]
    return items


def collect_test_sample():
    pat = re.compile(r"_(\d+)\.(jpg|jpeg|png)$", re.IGNORECASE)
    items = []
    for fname in os.listdir(TEST_DIR):
        m = pat.search(fname)
        if m and m.group(1) in FOLDER_TO_IDX:
            items.append((os.path.join(TEST_DIR, fname), FOLDER_TO_IDX[m.group(1)]))
    random.shuffle(items)
    return items[:TEST_SAMPLE]


def load_full(path):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img.set_shape([None, None, 3])
    return tf.cast(img, tf.float32)


def augment(img):
    h, w = tf.shape(img)[0], tf.shape(img)[1]
    m = tf.minimum(h, w)
    side = tf.cast(tf.cast(m, tf.float32) * tf.random.uniform([], 0.4, 1.0), tf.int32)
    side = tf.minimum(tf.maximum(side, 32), m)
    img = tf.image.random_crop(img, [side, side, 3])
    img = tf.image.resize(img, IMG) / 255.0
    img = tf.image.random_flip_left_right(img)
    img = tf.image.random_flip_up_down(img)
    img = tf.image.rot90(img, k=tf.random.uniform([], 0, 4, dtype=tf.int32))
    img = tf.image.random_brightness(img, 0.2)
    img = tf.image.random_contrast(img, 0.7, 1.3)
    img = tf.image.random_saturation(img, 0.6, 1.4)
    img = tf.image.random_hue(img, 0.03)
    r = tf.random.uniform([], 64, 224, dtype=tf.int32)
    img = tf.image.resize(tf.image.resize(img, [r, r]), IMG)
    return tf.clip_by_value(img, 0.0, 1.0)


def make_train_ds(items):
    random.shuffle(items)
    paths = [p for p, _ in items]
    labels = [l for _, l in items]
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(lambda p, l: (augment(load_full(p)), l), num_parallel_calls=AUTOTUNE)
    return ds.shuffle(2048, seed=SEED).batch(BATCH).prefetch(AUTOTUNE)


def make_eval_ds(items):
    paths = [p for p, _ in items]
    labels = [l for _, l in items]
    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    ds = ds.map(lambda p, l: (tf.image.resize(load_full(p), IMG) / 255.0, l),
                num_parallel_calls=AUTOTUNE)
    return ds.batch(BATCH).prefetch(AUTOTUNE)


def acc(model, items):
    if not items:
        return float("nan")
    return float(model.evaluate(make_eval_ds(items), verbose=0)[1])


if __name__ == "__main__":
    if not os.path.isdir(REAL_DIR):
        raise SystemExit(f"Folder not found: {REAL_DIR}")

    real_train, real_val = collect_real()
    if len(real_train) < 30:
        raise SystemExit("Fewer than 30 real training photos found - add more first.")
    orig = collect_original()
    test_items = collect_test_sample()
    print(f"\nReal train: {len(real_train)} (x{REAL_REPEAT} repeats) | Real held-out: {len(real_val)} "
          f"| Original mix-in: {len(orig)} | Test sample: {len(test_items)}")

    model = tf.keras.models.load_model(SRC_MODEL, compile=False)
    model.compile(optimizer=tf.keras.optimizers.Adam(LR),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    print("\n--- BEFORE fine-tuning ---")
    before_real = acc(model, real_val)
    before_test = acc(model, test_items)
    print(f"Held-out real photos : {before_real:.3f}")
    print(f"Original Test sample : {before_test:.3f}")

    train_ds = make_train_ds(real_train * REAL_REPEAT + orig)
    val_ds = make_eval_ds(real_val) if real_val else None
    callbacks = []
    if val_ds is not None:
        callbacks.append(tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=4, restore_best_weights=True))
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

    print("\n--- AFTER fine-tuning ---")
    after_real = acc(model, real_val)
    after_test = acc(model, test_items)
    print(f"Held-out real photos : {before_real:.3f} -> {after_real:.3f}")
    print(f"Original Test sample : {before_test:.3f} -> {after_test:.3f}")

    model.save(OUT_MODEL)
    print(f"\nSaved: {OUT_MODEL}")
    print("To use it, set SPECIES_MODEL_PATH in predict.py to 'wood_species_model_real.h5'.")