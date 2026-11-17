"""Phase 4.3 - Fine-tune the trained MobileNetV2 species model.
Baseline (frozen backbone): 73.94% test accuracy.
Saves to models/wood_species_model_ft.h5 (baseline file is NOT overwritten)."""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from preprocess_wood_species import (
    build_train_val_datasets, build_test_dataset, get_class_names,
    prepare, compute_class_weights,
)

MODELS_DIR = "models"
BASE_PATH = os.path.join(MODELS_DIR, "wood_species_model.h5")
FT_PATH = os.path.join(MODELS_DIR, "wood_species_model_ft.h5")
UNFREEZE_LAST = 30     # number of backbone layers to unfreeze
LEARNING_RATE = 1e-5
EPOCHS = 15
BASELINE_ACC = 73.94

class_names = get_class_names()
print("Class order:", class_names)

print("\nLoading datasets...")
raw_train, raw_val = build_train_val_datasets()
assert raw_train.class_names == class_names, "Class order mismatch!"
raw_test = build_test_dataset(class_names)

# Softer class weights: square root of the 'balanced' weights
cw = compute_class_weights(raw_train)
cw = {k: float(v) ** 0.5 for k, v in cw.items()}
print("Softened class weights:", {k: round(v, 2) for k, v in cw.items()})

train_ds = prepare(raw_train, training=True)
val_ds = prepare(raw_val, training=False)
test_ds = prepare(raw_test, training=False)

print("\nLoading baseline model...")
model = tf.keras.models.load_model(BASE_PATH, compile=False)

base = next(l for l in model.layers if isinstance(l, tf.keras.Model))
base.trainable = True
for layer in base.layers[:-UNFREEZE_LAST]:
    layer.trainable = False
for layer in base.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
print(f"Backbone layers: {len(base.layers)}, "
      f"trainable: {sum(l.trainable for l in base.layers)}")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

callbacks = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=4, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint(
        FT_PATH, monitor="val_accuracy", save_best_only=True),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7),
]

print(f"\nFine-tuning for up to {EPOCHS} epochs...")
history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS,
                    class_weight=cw, callbacks=callbacks)

# ---- Evaluate on the test set ----
print("\nEvaluating fine-tuned model on test set...")
y_true, y_pred = [], []
for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))
    y_true.extend(labels.numpy())
y_true, y_pred = np.array(y_true), np.array(y_pred)

acc = (y_true == y_pred).mean() * 100
print(f"\nTest images: {len(y_true)}")
print(f"Baseline test accuracy:   {BASELINE_ACC:.2f}%")
print(f"Fine-tuned test accuracy: {acc:.2f}%")
print(classification_report(y_true, y_pred, target_names=class_names))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Fine-tuned Wood Species Model (Test Set)")
plt.tight_layout()
out = os.path.join(MODELS_DIR, "confusion_matrix_ft.png")
plt.savefig(out, dpi=150)
print("Saved:", os.path.abspath(out))
print("Model saved to:", os.path.abspath(FT_PATH))