"""Single Source of Truth for Furniture Catalog (31 Precision Pieces).
Contains definitions, metadata, images, structural demands, blueprints, and cut lists.
"""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "furniture.data.json")

if os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        FURNITURE_DATA = json.load(f)
else:
    FURNITURE_DATA = []

FURNITURE_BY_ID = {f["id"]: f for f in FURNITURE_DATA}

def get_all_furniture():
    return FURNITURE_DATA

def get_furniture_by_id(furniture_id):
    return FURNITURE_BY_ID.get(furniture_id, FURNITURE_DATA[0] if FURNITURE_DATA else None)

def get_categories():
    seen = []
    for f in FURNITURE_DATA:
        cat = f.get("category", "General")
        if cat not in seen:
            seen.append(cat)
    return seen

def get_category_counts():
    counts = {}
    for f in FURNITURE_DATA:
        cat = f.get("category", "General")
        counts[cat] = counts.get(cat, 0) + 1
    return counts
