"""Furniture Recommender Module.
Integrates furniture_data, woods_data, and scoring_engine.
Maintains backward compatibility while providing dynamic, data-driven catalog counts.
"""
import os
from furniture_data import (
    FURNITURE_DATA,
    FURNITURE_BY_ID,
    get_all_furniture,
    get_categories,
    get_category_counts
)
from woods_data import WOODS_DATABASE, WOODS_BY_ID
import scoring_engine

# Build Dynamic Category List with Real Computed Counts
TOTAL_ITEMS = len(FURNITURE_DATA)
CATEGORY_COUNTS = get_category_counts()

CATEGORIES = [f"All ({TOTAL_ITEMS})"]
for cat in get_categories():
    cnt = CATEGORY_COUNTS.get(cat, 0)
    CATEGORIES.append(f"{cat} ({cnt})")

def clean_category(cat_str):
    """Strip count suffix from category string, e.g. 'Seating & Chairs (6)' -> 'Seating & Chairs'."""
    if not cat_str or cat_str.startswith("All"):
        return "All"
    if " (" in cat_str:
        return cat_str.split(" (")[0].strip()
    return cat_str.strip()

# Build FURNITURE_KNOWLEDGE for full backward-compatibility with UI tabs
FURNITURE_KNOWLEDGE = {}
for item in FURNITURE_DATA:
    fid = item["id"]
    demands = item.get("structuralDemands", {})
    
    # Map architectural designs
    designs_list = []
    for d in item.get("architecturalDesigns", []):
        designs_list.append({
            "title": d.get("name", "Architectural Blueprint"),
            "badge": d.get("style", "Studio Standard"),
            "description": f"Engineered solid wood joinery specification for {item['name']}.",
            "dimensions": d.get("dimensions", "Standard Ergonomic Scale"),
            "recommended_joinery": d.get("joinery", "Traditional Mortise & Tenon"),
            "recommended_finish": d.get("finish", "Hardwax Oil or Danish Oil"),
            "best_wood": d.get("recommendedWood", "Teak, White Oak, Black Walnut"),
            "load_capacity": demands.get("loadType", "Standard residential load"),
            "blueprint_tips": item.get("rules", ["Always maintain proper timber moisture content."])[0]
        })

    FURNITURE_KNOWLEDGE[fid] = {
        "id": fid,
        "name": item["name"],
        "full_name": item.get("full_name", item["name"]),
        "category": item["category"],
        "icon": item["icon"],
        "image": item["image"],
        "rel_image": item.get("rel_image", f"assets/furniture/{fid}.jpg"),
        "tagline": item["tagline"],
        "overview": item["description"],
        "structuralDemands": demands,
        "stress_profile": {
            "min_mor": f"≥ {demands.get('minMOR', 80)} MPa",
            "load_type": demands.get("loadType", "Standard domestic load"),
            "density_range": demands.get("densityRange", "600 – 760 kg/m³"),
            "target_mc": demands.get("targetMC", "8% – 10%"),
            "critical_zone": demands.get("criticalZone", "Structural joints"),
            "recommended_cut": demands.get("recommendedCut", "Quarter-sawn or Rift-sawn")
        },
        "recommended_woods": scoring_engine.recommend_woods(fid),
        "recommended_designs": designs_list,
        "carpentry_rules": item.get("rules", [])
    }

def get_all_categories():
    """Returns dynamic category strings with real computed item counts."""
    return CATEGORIES

def get_furniture_keys(category=None):
    """Retrieve keys filtered by category (supports both 'Cat (N)' and 'Cat')."""
    clean_cat = clean_category(category)
    if clean_cat == "All":
        return list(FURNITURE_KNOWLEDGE.keys())
    return [k for k, v in FURNITURE_KNOWLEDGE.items() if v["category"] == clean_cat]

def get_furniture_item(fid):
    """Retrieve single item by id with fallback."""
    return FURNITURE_KNOWLEDGE.get(fid, FURNITURE_KNOWLEDGE["wooden_chair"])

def search_furniture(query="", category="All"):
    """Filter and search catalog dynamically."""
    clean_cat = clean_category(category)
    q = (query or "").strip().lower()
    items = list(FURNITURE_KNOWLEDGE.items())
    
    if clean_cat != "All":
        items = [(k, v) for k, v in items if v["category"] == clean_cat]
        
    if not q:
        return [k for k, _ in items]
        
    return [
        k for k, v in items
        if q in v["name"].lower() or q in v["full_name"].lower() or q in v["category"].lower() or q in v["tagline"].lower() or q in v["overview"].lower()
    ]

def recommend_woods(furniture_id, options=None):
    """Delegates to decoupled scoring engine."""
    return scoring_engine.recommend_woods(furniture_id, options)

def get_other_designs_for_wood(wood_id, threshold=70.0, options=None):
    """Delegates to two-way explorer scoring engine."""
    return scoring_engine.get_other_designs_for_wood(wood_id, threshold, options)
