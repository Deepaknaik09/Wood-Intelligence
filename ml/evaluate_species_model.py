"""Re-evaluate the already-trained species model with correctly aligned labels."""
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from preprocess_wood_species import (
    build_test_dataset, get_class_names, prepare,
)

MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "wood_species_model.h5")

class_names = get_class_names()
print("Class order used in training:", class_names)

model = tf.keras.models.load_model(MODEL_PATH)
test_ds = prepare(build_test_dataset(class_names), training=False)

y_true, y_pred = [], []
for images, labels in test_ds:
    preds = model.predict(images, verbose=0)
    y_pred.extend(np.argmax(preds, axis=1))
    y_true.extend(labels.numpy())

y_true, y_pred = np.array(y_true), np.array(y_pred)
print(f"\nTest images: {len(y_true)}")
print(f"Test accuracy: {(y_true == y_pred).mean() * 100:.2f}%\n")
print(classification_report(y_true, y_pred, target_names=class_names))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Wood Species (Test Set, corrected)")
plt.tight_layout()
out = os.path.join(MODELS_DIR, "confusion_matrix_corrected.png")
plt.savefig(out, dpi=150)
print("Saved:", os.path.abspath(out))