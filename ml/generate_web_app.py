"""Generator for the complete upgraded Wood Intelligence Web App (index.html)."""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

with open(os.path.join(BASE_DIR, "furniture.data.json"), "r", encoding="utf-8") as f:
    furniture_json = f.read()

with open(os.path.join(BASE_DIR, "woods.data.json"), "r", encoding="utf-8") as f:
    woods_json = f.read()

# Read the pure scoring engine code from js/scoring_engine.js
with open(os.path.join(PROJECT_ROOT, "js", "scoring_engine.js"), "r", encoding="utf-8") as f:
    scoring_engine_code = f.read()

print("Read data and scoring engine successfully.")

