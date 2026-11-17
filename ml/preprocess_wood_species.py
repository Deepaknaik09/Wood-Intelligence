"""
Phase 3 - Preprocessing Script
Wood Species Dataset (Zenodo 2545611)

Builds a TensorFlow data pipeline:
- Loads Train/ (class-subfolder structure) and Test/ (flat, class in filename)
- Resizes images to 224x224, normalizes pixel values
- Applies data augmentation (train only): flip, rotation, zoom, contrast
- Computes class weights to handle the imbalance we found
  (Class 3 has ~5x more images than Class 2)

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python preprocess_wood_species.py
"""

import os
import re
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.utils.class_weight import compute_class_weight

# ---- CONFIG ----
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
DATASET_ROOT = os.path.join("..", "datasets", "wood_species", "Wood Dataset")
TRAIN_DIR = os.path.join(DATASET_ROOT, "Train")
TEST_DIR = os.path.join(DATASET_ROOT, "Test")


def get_class_names():
    """Class order exactly as Keras assigns it: folder names sorted as strings."""
    return sorted(
        d for d in os.listdir(TRAIN_DIR)
        if os.path.isdir(os.path.join(TRAIN_DIR, d))
    )


def build_train_val_datasets():
    """Load Train/ using Keras' built-in directory loader (80/20 train/val split)."""
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        validation_split=0.2,
        subset="training",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int"
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        validation_split=0.2,
        subset="validation",
        seed=42,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int"
    )
    return train_ds, val_ds


def build_test_dataset(class_names=None):
    """Test/ is flat with class encoded as _<N>.jpg in the filename.
    Labels are mapped through the TRAINING class order so they match the model."""
    if class_names is None:
        class_names = get_class_names()
    name_to_index = {name: i for i, name in enumerate(class_names)}

    pattern = re.compile(r"_(\d+)\.(jpg|jpeg|png)$", re.IGNORECASE)
    filepaths, labels = [], []
    for fname in sorted(os.listdir(TEST_DIR)):
        match = pattern.search(fname)
        if match and match.group(1) in name_to_index:
            filepaths.append(os.path.join(TEST_DIR, fname))
            labels.append(name_to_index[match.group(1)])

    def load_and_preprocess(path, label):
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        img = tf.image.resize(img, IMG_SIZE)
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((filepaths, labels))
    ds = ds.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE)
    return ds


# ---- Data augmentation (applied only to training data) ----
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
    layers.RandomContrast(0.1),
])

# ---- Normalization (applied to all splits) ----
normalization = layers.Rescaling(1.0 / 255)


def prepare(ds, training=False):
    if training:
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y),
                    num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.map(lambda x, y: (normalization(x), y),
                num_parallel_calls=tf.data.AUTOTUNE)
    return ds.prefetch(tf.data.AUTOTUNE)


def compute_class_weights(train_ds):
    """Compute class weights to counter the imbalance (Class 3 has ~5x Class 2)."""
    all_labels = []
    for _, labels in train_ds.unbatch():
        all_labels.append(labels.numpy())
    all_labels = np.array(all_labels)
    classes = np.unique(all_labels)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=all_labels)
    return dict(zip(classes, weights))


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 3 - WOOD SPECIES PREPROCESSING")
    print("=" * 60)

    print("\nLoading Train/Validation split...")
    raw_train_ds, raw_val_ds = build_train_val_datasets()
    class_names = raw_train_ds.class_names
    print(f"Classes found: {class_names}")

    print("\nLoading Test set (flat folder)...")
    raw_test_ds = build_test_dataset(class_names)

    print("\nComputing class weights (to fix the imbalance)...")
    class_weights = compute_class_weights(raw_train_ds)
    print("Class weights:")
    for cls, w in class_weights.items():
        print(f"  Class {class_names[cls]}: weight = {w:.3f}")

    print("\nApplying augmentation + normalization...")
    train_ds = prepare(raw_train_ds, training=True)
    val_ds = prepare(raw_val_ds, training=False)
    test_ds = prepare(raw_test_ds, training=False)

    print("\nSanity check - pulling one batch from each split:")
    for name, ds in [("Train", train_ds), ("Validation", val_ds), ("Test", test_ds)]:
        images, labels = next(iter(ds))
        print(f"  {name}: batch shape = {images.shape}, "
              f"pixel range = [{images.numpy().min():.2f}, {images.numpy().max():.2f}]")

    print("\nPhase 3 preprocessing pipeline built and verified successfully.")
    print("Use train_ds, val_ds, test_ds, and class_weights in Phase 4 (model training).")