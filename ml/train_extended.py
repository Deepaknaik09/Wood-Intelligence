"""Phase 6c - Extend the species model with the WSID dataset (7 extra species).

Run from the ml folder with the venv active (finetune_real.py must be in the same folder):
    python train_extended.py

Result: models/wood_species_model_ext.h5 + models/labels_ext.json  (19 classes)
Classes 1-12 = original dataset, 13-19 = WSID (Akashmoni, Eucalyptus, Kathal,
Loha, Mahogany, Minjiri, Rain tree). Old models are NOT touched.
"""
import os
import json
import random
import tensorflow as tf

# reuse helpers from finetune_real.py (importing it also sets the random seeds)
from finetune_real import (BASE, MODELS_DIR, TRAIN_DIR, FOLDER_TO_IDX, list_images,
                           collect_real, collect_test_sample, make_train_ds, make_eval_ds)

WSID_ROOT = os.path.join(BASE, "..", "datasets", "wsid", "wood")
WSID_TRAIN = os.path.join(WSID_ROOT, "train")
WSID_TEST = os.path.join(WSID_ROOT, "test")

# (new folder id, accepted folder-name spellings, lowercase, no spaces)
WSID_CLASSES = [
    ("13", ["akashmoni"]),
    ("14", ["eucalyptus", "eucaliptus"]),
    ("15", ["kathal"]),
    ("16", ["loha"]),
    ("17", ["mehogany", "mahogany", "mehogoni"]),
    ("18", ["minjiri"]),
    ("19", ["raintree"]),
]

ORIG_PER_CLASS = 300     # original-dataset images per class
WSID_PER_CLASS = 300     # WSID train images per class (train folder is augmented copies)
REAL_REPEAT = 4
EPOCHS = 12
LR = 5e-5

SRC_CANDIDATES = ["wood_species_model_real.h5", "wood_species_model_ft.h5"]
OUT_MODEL = os.path.join(MODELS_DIR, "wood_species_model_ext.h5")
OUT_LABELS = os.path.join(MODELS_DIR, "labels_ext.json")


def find_dir(parent, aliases):
    for d in os.listdir(parent):
        if os.path.isdir(os.path.join(parent, d)) and d.lower().replace(" ", "") in aliases:
            return os.path.join(parent, d)
    return None


def collect_orig():
    items = []
    for folder_id, idx in FOLDER_TO_IDX.items():
        files = list_images(os.path.join(TRAIN_DIR, folder_id))
        random.shuffle(files)
        items += [(p, idx) for p in files[:ORIG_PER_CLASS]]
    return items


def collect_wsid(new_idx):
    train, test = [], []
    print("WSID images per class (train sample / test):")
    for fid, aliases in WSID_CLASSES:
        idx = new_idx[fid]
        tdir = find_dir(WSID_TRAIN, aliases)
        vdir = find_dir(WSID_TEST, aliases)
        if tdir is None:
            raise SystemExit(f"WSID train folder not found for {aliases} in {WSID_TRAIN}")
        files = list_images(tdir)
        random.shuffle(files)
        tr = [(p, idx) for p in files[:WSID_PER_CLASS]]
        te = [(p, idx) for p in list_images(vdir)] if vdir else []
        train += tr
        test += te
        print(f"  class {fid}: {len(tr)} / {len(te)}   ({os.path.basename(tdir)})")
    return train, test


def extend_model(src_path, n_new):
    """Replace the final Dense layer with a larger one; keep the old class weights."""
    model = tf.keras.models.load_model(src_path, compile=False)
    old = next(l for l in reversed(model.layers) if isinstance(l, tf.keras.layers.Dense))
    ow, ob = old.get_weights()
    n_old = ow.shape[1]
    new_dense = tf.keras.layers.Dense(n_new, activation="softmax", name="species_out")
    out = new_dense(old.input)
    new_model = tf.keras.Model(model.inputs, out)
    nw, nb = new_dense.get_weights()
    nw[:, :n_old] = ow
    nb[:n_old] = ob
    new_dense.set_weights([nw, nb])
    return new_model


if __name__ == "__main__":
    if not os.path.isdir(WSID_TRAIN):
        raise SystemExit(f"WSID folder not found: {WSID_TRAIN}")

    # label map: keep the old order for classes 0-11, append the new ones
    with open(os.path.join(MODELS_DIR, "labels.json")) as f:
        new_labels = json.load(f)                    # {"0": "1", ...}
    n_old = len(new_labels)
    for i, (fid, _) in enumerate(WSID_CLASSES):
        new_labels[str(n_old + i)] = fid
    new_idx = {v: int(k) for k, v in new_labels.items()}
    n_total = len(new_labels)

    real_train, real_val = collect_real()            # must be the first random call
    orig = collect_orig()
    wsid_train, wsid_test = collect_wsid(new_idx)
    orig_test = collect_test_sample()
    print(f"\nReal train {len(real_train)} (x{REAL_REPEAT}) | Orig mix-in {len(orig)} | "
          f"WSID train {len(wsid_train)}")
    print(f"Held-out: real {len(real_val)} | WSID test {len(wsid_test)} | orig test {len(orig_test)}")

    src = next((os.path.join(MODELS_DIR, n) for n in SRC_CANDIDATES
                if os.path.exists(os.path.join(MODELS_DIR, n))), None)
    if src is None:
        raise SystemExit("No source model found in models/")
    print(f"\nStarting from: {os.path.basename(src)}  ->  {n_total} classes")
    model = extend_model(src, n_total)
    model.compile(optimizer=tf.keras.optimizers.Adam(LR),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    train_ds = make_train_ds(real_train * REAL_REPEAT + orig + wsid_train)
    val_items = real_val + wsid_test + orig_test[:300]
    val_ds = make_eval_ds(val_items)
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS,
              callbacks=[tf.keras.callbacks.EarlyStopping(
                  monitor="val_accuracy", patience=4, restore_best_weights=True)])

    print("\n--- FINAL ACCURACY (best epoch) ---")
    for name, items in [("Original dataset test", orig_test),
                        ("Your real photos (held-out)", real_val),
                        ("WSID test (7 new species)", wsid_test)]:
        a = float(model.evaluate(make_eval_ds(items), verbose=0)[1])
        print(f"{name:30s}: {a:.3f}")

    model.save(OUT_MODEL)
    with open(OUT_LABELS, "w") as f:
        json.dump(new_labels, f, indent=2)
    print(f"\nSaved: {OUT_MODEL}\nSaved: {OUT_LABELS}")