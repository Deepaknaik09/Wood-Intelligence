"""Decoupled, Pure Scoring Engine for Wood Recommendations.
Computes deterministic, multi-criteria suitability rankings for furniture pieces.
No UI code inside.
"""
from woods_data import WOODS_DATABASE, WOODS_BY_ID
from furniture_data import FURNITURE_DATA, FURNITURE_BY_ID

def norm_target(val, baseline_val, optimal_val):
    """Calibrated normalization: maps baseline -> 0.2, optimal -> 1.0."""
    if val <= baseline_val:
        return 0.2
    if val >= optimal_val:
        return 1.0
    return 0.2 + 0.8 * ((val - baseline_val) / (optimal_val - baseline_val))

def get_wood_normalized_metrics(wood):
    """Returns dict of 0-1 normalized engineering metrics calibrated for fine furniture."""
    cost_map = {1: 1.0, 2: 0.88, 3: 0.75, 4: 0.60, 5: 0.50}
    return {
        "mor": norm_target(wood["mor"], 50.0, 115.0),
        "hardness": norm_target(wood["hardness"], 1500.0, 6800.0),
        "stability": norm_target(wood["shrinkage"]["stability_score"], 5.0, 9.6),
        "durability": norm_target(wood["durability"], 3.5, 9.5),
        "workability": norm_target(wood["workability"], 4.0, 9.5),
        "finish": norm_target(wood["finishQuality"], 6.5, 9.8),
        "sustainability": norm_target(wood["sustainability"], 5.0, 10.0),
        "budget": cost_map.get(wood["costTier"], 0.7),
        "availability": norm_target(wood["availabilityInIndia"], 5.5, 9.8)
    }

def get_base_category_weights(category):
    """Baseline engineering weights per furniture category."""
    if category == "Seating & Chairs":
        return {
            "mor": 0.32,
            "hardness": 0.22,
            "stability": 0.16,
            "workability": 0.18,
            "finish": 0.12,
            "durability": 0.00
        }
    elif category == "Tables & Desks":
        return {
            "mor": 0.15,
            "hardness": 0.28,
            "stability": 0.30,
            "workability": 0.12,
            "finish": 0.15,
            "durability": 0.00
        }
    elif category == "Beds & Bedroom":
        return {
            "mor": 0.30,
            "hardness": 0.18,
            "stability": 0.26,
            "workability": 0.14,
            "finish": 0.12,
            "durability": 0.00
        }
    elif category == "Storage & Shelves":
        return {
            "mor": 0.16,
            "hardness": 0.14,
            "stability": 0.36,
            "workability": 0.20,
            "finish": 0.14,
            "durability": 0.00
        }
    elif category == "Architectural & Frames":
        return {
            "mor": 0.10,
            "hardness": 0.15,
            "stability": 0.35,
            "workability": 0.18,
            "finish": 0.10,
            "durability": 0.12
        }
    else:
        return {
            "mor": 0.20,
            "hardness": 0.20,
            "stability": 0.20,
            "workability": 0.20,
            "finish": 0.20,
            "durability": 0.00
        }

FURNITURE_FIT = {
    'wooden_chair': ['white_ash', 'white_oak', 'beech', 'teak', 'african_padauk'],
    'dining_chair': ['beech', 'white_ash', 'white_oak', 'black_walnut', 'teak'],
    'armchair': ['black_walnut', 'white_oak', 'teak', 'sheesham', 'mahogany'],
    'stool': ['hard_maple', 'white_ash', 'beech', 'acacia', 'rubberwood'],
    'bench': ['sal', 'white_ash', 'white_oak', 'acacia', 'eucalyptus'],
    'wooden_sofa_frame': ['sheesham', 'teak', 'sal', 'eucalyptus', 'white_oak'],
    'dining_table': ['teak', 'black_walnut', 'sheesham', 'white_oak', 'black_cherry'],
    'coffee_table': ['black_walnut', 'mango', 'teak', 'sheesham', 'wenge'],
    'study_table': ['hard_maple', 'bamboo', 'white_oak', 'rubberwood', 'teak'],
    'desk': ['black_walnut', 'mahogany', 'white_oak', 'hard_maple', 'sapele'],
    'side_table': ['black_cherry', 'teak', 'mango', 'sheesham', 'black_walnut'],
    'console_table': ['mahogany', 'mango', 'wenge', 'teak', 'black_walnut'],
    'dining_set': ['sheesham', 'teak', 'white_oak', 'beech', 'african_padauk'],
    'bed_frame': ['sheesham', 'teak', 'mahogany', 'sal', 'rubberwood'],
    'bunk_bed': ['sal', 'rubberwood', 'hard_maple', 'teak', 'eucalyptus'],
    'cot': ['hard_maple', 'sheesham', 'teak', 'jackfruit', 'rubberwood'],
    'bedside_table': ['black_cherry', 'black_walnut', 'teak', 'yellow_birch', 'mango'],
    'dressing_table': ['haldu', 'black_walnut', 'sheesham', 'black_cherry', 'teak'],
    'wardrobe': ['deodar', 'teak', 'sheesham', 'mahogany', 'white_oak'],
    'cupboard': ['deodar', 'teak', 'white_oak', 'yellow_birch', 'rubberwood'],
    'cabinet': ['sheesham', 'teak', 'white_oak', 'black_cherry', 'mahogany'],
    'bookshelf': ['white_oak', 'hard_maple', 'white_ash', 'red_oak', 'bamboo'],
    'wall_shelf': ['bamboo', 'mango', 'white_oak', 'poplar', 'marupa'],
    'tv_unit': ['sheesham', 'teak', 'black_walnut', 'mango', 'wenge'],
    'drawer_chest': ['black_cherry', 'deodar', 'yellow_birch', 'teak', 'beech'],
    'shoe_rack': ['acacia', 'rubberwood', 'deodar', 'mango', 'yellow_birch'],
    'door': ['teak', 'deodar', 'sal', 'andaman_padauk', 'african_padauk'],
    'window_frame': ['deodar', 'teak', 'sal', 'western_red_cedar', 'andaman_padauk'],
    'mirror_frame': ['haldu', 'black_walnut', 'black_cherry', 'mango', 'sheesham'],
    'photo_frame': ['black_cherry', 'marupa', 'poplar', 'haldu', 'beech'],
    'wooden_partition': ['bamboo', 'deodar', 'haldu', 'teak', 'sheesham']
}

def generate_reasons_and_tradeoffs(wood, furniture_item, options):
    """Generates plain-English reasons and trade-offs for recommended wood."""
    reasons = []
    tradeoffs = []
    category = furniture_item.get("category", "")
    demands = furniture_item.get("structuralDemands", {})
    min_mor = demands.get("minMOR", 80)
    
    f_id = furniture_item.get("id", "").replace('-', '_')
    premier_list = FURNITURE_FIT.get(f_id, [])
    if wood["id"] in premier_list:
        reasons.append(f"Classically favored master timber for handcrafted {furniture_item.get('name', 'furniture').lower()} joinery.")
    
    # 1. Structural Suitability Reasons
    if wood["mor"] >= min_mor:
        reasons.append(f"High flexural strength ({wood['mor']:.1f} MPa MOR) comfortably exceeds structural requirement of {min_mor} MPa.")
    elif wood["mor"] >= 80:
        reasons.append(f"Adequate bending strength ({wood['mor']:.1f} MPa MOR) for standard residential load cycles.")

    if category in ["Seating & Chairs", "Beds & Bedroom"] and wood["mor"] >= 100:
        reasons.append(f"Excellent shock resistance resists cyclic racking forces on structural leg and post tenons.")

    if category in ["Tables & Desks", "Storage & Shelves"] and wood["shrinkage"]["stability_score"] >= 8.5:
        reasons.append(f"Superior dimensional stability (stability score {wood['shrinkage']['stability_score']}/10) prevents tabletop cupping and door binding.")

    if wood["hardness"] >= 5000:
        reasons.append(f"High Janka hardness ({wood['hardness']} N) provides robust resistance against everyday dents and surface scratches.")

    if wood["workability"] >= 8.5:
        reasons.append(f"Exceptional workability ({wood['workability']}/10) delivers razor-sharp joinery shoulders and crisp edge profiles.")

    if wood["finishQuality"] >= 9.0:
        reasons.append(f"World-class grain chatoyance ({wood['finishQuality']}/10) takes high-end architectural oil and wax polishes.")

    if options.get("environment") == "Outdoor" and wood["durability"] >= 8.0:
        reasons.append(f"Immense natural heartwood extractives ({wood['durability']}/10 durability) defend against exterior rot and fungal decay.")

    if wood["sustainability"] >= 9.0:
        reasons.append(f"High eco-sustainability rating ({wood['sustainability']}/10) sourced from fast-growing managed forestry or plantation byproducts.")

    if wood["costTier"] <= 2 and options.get("budget") in ["Low", "Medium"]:
        reasons.append(f"Favorable commercial cost tier (Tier {wood['costTier']}) offers maximum economic yield per board foot.")

    # Fallback reason
    if not reasons:
        reasons.append(f"Balanced density ({wood['density']} kg/m³) and proven stability for handcrafted cabinetry.")

    # 2. Tradeoffs
    if wood["costTier"] >= 4:
        tradeoffs.append(f"Premium luxury cost tier (Tier {wood['costTier']}); commands higher raw lumber budget.")

    if wood["durability"] < 5.0:
        tradeoffs.append(f"Non-durable against moisture ({wood['durability']}/10); strictly designated for interior climate-controlled environments.")

    if wood["workability"] <= 6.8:
        tradeoffs.append(f"Dense or interlocked grain ({wood['workability']}/10 workability) requires sharp carbide tooling and slow feed rates.")

    if wood["availabilityInIndia"] < 7.0:
        tradeoffs.append(f"Imported specialty lumber; regional availability in India may be limited to premier timber yards.")

    if wood["shrinkage"]["volumetric"] >= 14.5:
        tradeoffs.append(f"Moderate volumetric movement ({wood['shrinkage']['volumetric']}%); requires careful 8–10% indoor moisture acclimation.")

    if not tradeoffs:
        tradeoffs.append("Readily available with balanced working properties; no major engineering drawbacks.")

    return reasons[:3], tradeoffs[:2]

def score_all_woods(furniture_id, options=None):
    """Scores all 28 woods for a given furniture piece deterministically."""
    options = options or {}
    budget_opt = options.get("budget", "All")
    priority_opt = options.get("priority", "Balanced")
    env_opt = options.get("environment", "Indoor")
    
    furniture_item = FURNITURE_BY_ID.get(furniture_id, FURNITURE_DATA[0])
    category = furniture_item.get("category", "")
    demands = furniture_item.get("structuralDemands", {})
    
    # 1. Start with base category weights
    weights = get_base_category_weights(category).copy()
    weights["sustainability"] = 0.05
    weights["budget"] = 0.05

    # 2. Apply per-item overrides from structuralDemands if specified
    if "weightImportance" in demands:
        weights["mor"] = max(weights["mor"], demands["weightImportance"])
    if "hardnessImportance" in demands:
        weights["hardness"] = demands["hardnessImportance"]
    if "stabilityImportance" in demands:
        weights["stability"] = demands["stabilityImportance"]

    # 3. Apply Environment Modifier
    if env_opt == "Outdoor":
        weights["durability"] = 0.40
        # Scale remaining weights down
        scale = 0.60 / sum(v for k, v in weights.items() if k != "durability")
        for k in weights:
            if k != "durability":
                weights[k] *= scale

    # 4. Apply User Priority Modifier
    if priority_opt == "Strength":
        weights["mor"] *= 2.2
        weights["hardness"] *= 1.8
    elif priority_opt == "Stability":
        weights["stability"] *= 2.5
    elif priority_opt == "Looks":
        weights["finish"] *= 2.5
    elif priority_opt == "Budget":
        weights["budget"] = 0.35
    elif priority_opt == "Eco":
        weights["sustainability"] = 0.35

    # Normalize weights to sum exactly to 1.0
    sum_w = sum(weights.values())
    if sum_w > 0:
        weights = {k: v / sum_w for k, v in weights.items()}

    # 5. Score every wood in the database
    scored_woods = []
    min_demanded_mor = demands.get("minMOR", 75)
    f_id = furniture_item.get("id", "").replace('-', '_')
    premier_list = FURNITURE_FIT.get(f_id, [])

    for wood in WOODS_DATABASE:
        norm = get_wood_normalized_metrics(wood)
        
        # Calculate raw weighted score
        raw_score = sum(norm.get(k, 0.0) * weights.get(k, 0.0) for k in weights)
        score_100 = raw_score * 100.0

        # Structural penalty if MOR is below critical minimum
        if wood["mor"] < min_demanded_mor:
            deficit_pct = (min_demanded_mor - wood["mor"]) / min_demanded_mor
            score_100 -= (deficit_pct * 30.0)

        # Outdoor rot penalty
        if env_opt == "Outdoor" and wood["durability"] < 6.0:
            score_100 -= 40.0

        # Budget constraint adjustments
        if budget_opt == "Low":
            if wood["costTier"] >= 4:
                score_100 -= 28.0
            elif wood["costTier"] <= 2:
                score_100 += 8.0
        elif budget_opt == "Medium":
            if wood["costTier"] == 5:
                score_100 -= 14.0
            elif wood["costTier"] in [2, 3]:
                score_100 += 5.0
        elif budget_opt == "High":
            if wood["costTier"] >= 4:
                score_100 += 5.0

        # Craftsmanship design suitability bonus
        if wood["id"] in premier_list:
            pos = premier_list.index(wood["id"])
            bonus = 20.0 - (pos * 3.75)
            score_100 += bonus

        score_100 = max(10.0, min(99.4, score_100))
        final_score = round(score_100, 1)

        breakdown = {
            "strength": round(norm["mor"] * 100, 1),
            "hardness": round(norm["hardness"] * 100, 1),
            "stability": round(norm["stability"] * 100, 1),
            "durability": round(norm["durability"] * 100, 1),
            "workability": round(norm["workability"] * 100, 1),
            "finish": round(norm["finish"] * 100, 1),
            "cost_score": round(norm["budget"] * 100, 1),
            "sustainability": round(norm["sustainability"] * 100, 1)
        }

        reasons, tradeoffs = generate_reasons_and_tradeoffs(wood, furniture_item, options)

        scored_woods.append({
            "wood": wood,
            "score": final_score,
            "breakdown": breakdown,
            "reasons": reasons,
            "tradeoffs": tradeoffs
        })

    # 6. Sort deterministically: highest score first, ties broken by lower cost then availability
    scored_woods.sort(
        key=lambda x: (
            -x["score"],
            x["wood"]["costTier"],
            -x["wood"]["availabilityInIndia"],
            x["wood"]["name"]
        )
    )

    return scored_woods

def recommend_woods(furniture_id, options=None):
    """Returns top 5 recommended woods for given piece."""
    all_scored = score_all_woods(furniture_id, options)
    top_5 = all_scored[:5]
    for idx, item in enumerate(top_5):
        item["rank"] = idx + 1
        item["is_best_match"] = (idx == 0)
    return top_5

def get_other_designs_for_wood(wood_id, threshold=70.0, options=None):
    """Two-way explorer function: finds all furniture pieces where this wood scores >= threshold.
    
    Returns:
        dict: Grouped by category, sorted by descending score.
              e.g. { 'Seating & Chairs': [ { 'item': ..., 'score': 94.2 }, ... ], ... }
    """
    grouped_results = {}
    options = options or {}

    for item in FURNITURE_DATA:
        all_scored = score_all_woods(item["id"], options)
        wood_match = next((r for r in all_scored if r["wood"]["id"] == wood_id), None)
        if wood_match and wood_match["score"] >= threshold:
            cat = item["category"]
            if cat not in grouped_results:
                grouped_results[cat] = []
            grouped_results[cat].append({
                "item": item,
                "score": wood_match["score"]
            })

    # Sort items within each category by descending score
    for cat in grouped_results:
        grouped_results[cat].sort(key=lambda x: -x["score"])

    return grouped_results
