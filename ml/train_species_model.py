"""
Phase 4 - Wood Species Identification Model
Uses transfer learning (MobileNetV2 pretrained on ImageNet) fine-tuned
on the Wood Species Dataset (12 classes).

Reuses the data pipeline built in preprocess_wood_species.py.

Run this from inside the ml/ folder of your project:
    cd D:\\Main_Project\\wood-intelligence-project\\ml
    python train_species_model.py

Outputs (saved into ml/models/):
    wood_species_model.h5   - trained model
    labels.json              - class index -> species name mapping
    training_curves.png      - accuracy/loss over epochs
    confusion_matrix.png     - test set confusion matrix
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

from preprocess_wood_species import (
    build_train_val_datasets,
    build_test_dataset,
    prepare,
    compute_class_weights,
    IMG_SIZE,
)

MODELS_DIR = "models"
EPOCHS = 20


def build_model(num_classes):
    """MobileNetV2 backbone (frozen) + custom classification head."""
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # freeze pretrained weights

    inputs = layers.Input(shape=IMG_SIZE + (3,))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def plot_training_curves(history, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(history.history["accuracy"], label="Train")
    axes[0].plot(history.history["val_accuracy"], label="Validation")
    axes[0].set_title("Accuracy")
    axes[0].set_xlabel("Epoch")
    axes[0].legend()

    axes[1].plot(history.history["loss"], label="Train")
    axes[1].plot(history.history["val_loss"], label="Validation")
    axes[1].set_title("Loss")
    axes[1].set_xlabel("Epoch")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved training curves to: {os.path.abspath(out_path)}")


def evaluate_on_test(model, test_ds, class_names, out_path):
    y_true, y_pred = [], []
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0)
        y_pred.extend(np.argmax(preds, axis=1))
        y_true.extend(labels.numpy())

    print("\nClassification Report (Test Set):")
    print(classification_report(y_true, y_pred, target_names=class_names))

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix - Wood Species (Test Set)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"Saved confusion matrix to: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 4 - WOOD SPECIES MODEL TRAINING")
    print("=" * 60)

    os.makedirs(MODELS_DIR, exist_ok=True)

    print("\nLoading datasets...")
    raw_train_ds, raw_val_ds = build_train_val_datasets()
    class_names = raw_train_ds.class_names
    raw_test_ds = build_test_dataset()

    print(f"Classes ({len(class_names)}): {class_names}")

    print("\nComputing class weights...")
    class_weights = compute_class_weights(raw_train_ds)

    print("\nPreparing (augmenting + normalizing) datasets...")
    train_ds = prepare(raw_train_ds, training=True)
    val_ds = prepare(raw_val_ds, training=False)
    test_ds = prepare(raw_test_ds, training=False)

    print("\nBuilding model (MobileNetV2 transfer learning)...")
    model = build_model(num_classes=len(class_names))
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            os.path.join(MODELS_DIR, "wood_species_model.h5"),
            monitor="val_accuracy", save_best_only=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6
        ),
    ]

    print(f"\nTraining for up to {EPOCHS} epochs (early stopping enabled)...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
    )

    plot_training_curves(history, os.path.join(MODELS_DIR, "training_curves.png"))

    print("\nEvaluating on held-out test set...")
    evaluate_on_test(model, test_ds, class_names,
                      os.path.join(MODELS_DIR, "confusion_matrix.png"))

    # Save class index -> species name mapping (using the raw folder names as species IDs)
    labels_path = os.path.join(MODELS_DIR, "labels.json")
    with open(labels_path, "w") as f:
        json.dump({i: name for i, name in enumerate(class_names)}, f, indent=2)
    print(f"\nSaved labels.json to: {os.path.abspath(labels_path)}")

    print("\nPhase 4 complete. Model saved to models/wood_species_model.h5")
