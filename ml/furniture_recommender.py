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

# ---------------------------------------------------------------------------
# DEDICATED DESIGN PATTERN CATALOG (CURATED PER FURNITURE PIECE)
# ---------------------------------------------------------------------------
FURNITURE_DESIGN_PATTERNS = {
    "wooden_partition": [
        {
            "title": "Vertical Timber Baffle Screen",
            "badge": "Modern Japanese Lattice",
            "description": "Floor-to-ceiling rhythmic vertical louvers providing visual zoning while allowing free airflow and natural illumination.",
            "dimensions": "Width: 150 cm | Height: 240 cm | Slat Profile: 40 x 40 mm",
            "recommended_joinery": "Concealed floating mortise & tenon into ceiling/floor tracks",
            "recommended_finish": "Acoustic-enhancing Matte Hardwax Oil",
            "load_capacity": "Airflow draft & lateral knock resistance (80–120 kg lateral)",
            "blueprint_tips": "Select quarter-sawn stiles to prevent seasonal twisting; counter-bore bottom track for concealed leveling bolts.",
            "aesthetic_rhythm": "40mm timber stiles spaced with 30mm negative air gaps"
        },
        {
            "title": "Geometric Kumiko & Diamond Lattice Screen",
            "badge": "Heritage Artisan Fretwork",
            "description": "Intricate geometric fretwork panel inspired by classical joinery, creating semi-private luxury interiors with ambient light diffusion.",
            "dimensions": "Width: 120 cm | Height: 215 cm | Grid Unit: 65 x 65 mm",
            "recommended_joinery": "Precision half-lap interlocking fretwork in mortised perimeter stiles",
            "recommended_finish": "Hand-Rubbed Tung Oil with microcrystalline wax topcoat",
            "load_capacity": "Light-filtering decorative divider (50 kg lateral)",
            "blueprint_tips": "Gang-cut all half-lap notches on a dedicated crosscut sled with stop blocks to guarantee 0.2mm tolerances across the grid.",
            "aesthetic_rhythm": "18x35mm interlocking wooden laths in diagonal diamond tessellation"
        },
        {
            "title": "Tri-Fold Accordion Room Divider",
            "badge": "Mobile Architectural Screen",
            "description": "Portable three-leaf folding screen with chamfered inner panels and weighted bottom rails for self-standing stability.",
            "dimensions": "3 Panels (Each 50 cm W x 185 cm H) | Total Width: 150 cm",
            "recommended_joinery": "Double-acting brass pivot hinges with haul-lap stile and rail frames",
            "recommended_finish": "Two-Pack Polyurethane Satin or Natural Shellac",
            "load_capacity": "Free-standing mobile screen (stable on level flooring)",
            "blueprint_tips": "Add 25% extra mass to the bottom rail to lower center of gravity and prevent accidental tipping.",
            "aesthetic_rhythm": "Reversible 360-degree folding action with inset floating panels"
        },
        {
            "title": "Perforated Jali Architectural Panel",
            "badge": "Contemporary CNC Fusion",
            "description": "Architectural focal screen featuring organic geometric perforations that project artistic ambient shadows across the living area.",
            "dimensions": "Width: 140 cm | Height: 230 cm | Core Thickness: 32 mm",
            "recommended_joinery": "Deep rebate frame channel with bottom acoustic neoprene isolators",
            "recommended_finish": "Hardwax Polyx-Oil or Penetrating Teak Oil",
            "load_capacity": "Structural floor-to-ceiling room partition (150 kg lateral)",
            "blueprint_tips": "Allow a 5mm expansion channel along the upper track groove to absorb seasonal cross-grain timber movement.",
            "aesthetic_rhythm": "Continuous parametric lattice perforation with 50mm solid perimeter border"
        },
        {
            "title": "Open Display & Planter Room Divider",
            "badge": "Biophilic Modular Grid",
            "description": "Dual-aspect spatial divider with alternating open cubic display bays and integrated waterproof planter troughs.",
            "dimensions": "Width: 160 cm | Height: 195 cm | Depth: 32 cm",
            "recommended_joinery": "Stopped housing dado joints locked with blind hardwood dowels",
            "recommended_finish": "Moisture-Resistant Marine Osmo Polyx-Oil with sealed base",
            "load_capacity": "Heavy display storage and planter soil loads (160–220 kg)",
            "blueprint_tips": "Line interior planter troughs with HDPE or zinc trays to isolate moisture completely from primary structural joinery.",
            "aesthetic_rhythm": "Asymmetric open/closed shelving cubes with integrated plant pockets"
        }
    ]
}

def get_furniture_design_patterns(furniture_id: str, wood_id: str = None) -> list:
    """Returns various architectural design patterns specifically for the given furniture piece,
    dynamically enriched with timber engineering compatibility notes when wood_id is provided."""
    item = get_furniture_item(furniture_id)
    cat = item.get("category", "")
    
    # 1. Fetch tailored patterns if directly defined
    if furniture_id in FURNITURE_DESIGN_PATTERNS:
        base_patterns = FURNITURE_DESIGN_PATTERNS[furniture_id]
    else:
        # Category-level specialized architectural patterns
        if "Chair" in cat or "Seating" in cat:
            base_patterns = [
                {
                    "title": f"Scandinavian Wishbone Ergonomic {item['name']}",
                    "badge": "Nordic Minimalist",
                    "description": f"Ergonomic {item['name']} featuring continuous steam-bent crest rail, tapered round legs, and floating seat apron.",
                    "dimensions": "Width: 55 cm | Depth: 52 cm | Height: 78 cm | Seat Height: 45 cm",
                    "recommended_joinery": "Deep mortise & tenon corner leg joints with steam-bent crest rail tenons",
                    "recommended_finish": "Clear Ultra-Matte Polyurethane or Natural Danish Oil",
                    "load_capacity": "Cyclic dynamic seating loads (140–180 kg)",
                    "blueprint_tips": "Steam-bend crest rail at 100°C for 45 minutes; allow 48-hour form drying before tenoning.",
                    "aesthetic_rhythm": "Slender compound tapered legs with continuous flowing curved backrest"
                },
                {
                    "title": f"Mid-Century Sculptural {item['name']}",
                    "badge": "Organic Modernism",
                    "description": f"Sculpted hardwood {item['name']} with angular rear leg rake, floating apron, and lumbar support.",
                    "dimensions": "Width: 52 cm | Depth: 54 cm | Height: 82 cm | Seat Height: 46 cm",
                    "recommended_joinery": "Integral angled rear leg-to-backrest mortise with corner apron reinforcement cleats",
                    "recommended_finish": "Hand-Rubbed Tinted Hardwax Oil",
                    "load_capacity": "Everyday commercial dining loads (160 kg)",
                    "blueprint_tips": "Grain orientation on rear angled leg stiles must run continuous to resist racking shear.",
                    "aesthetic_rhythm": "Beveled undercut seat perimeter with floating side stretchers"
                },
                {
                    "title": f"Classic Windsor Spindle {item['name']}",
                    "badge": "Traditional Fine Joinery",
                    "description": f"Classic high-back {item['name']} with deep hand-scooped saddle seat and wedged through-tenon spindles.",
                    "dimensions": "Width: 54 cm | Depth: 56 cm | Height: 94 cm | Seat Height: 45 cm",
                    "recommended_joinery": "Wedged through-tenon legs and turned spindles locked with contrasting walnut wedges",
                    "recommended_finish": "Burnished Shellac with Carnauba Wax Polish",
                    "load_capacity": "Heavy daily cyclic loads (180 kg)",
                    "blueprint_tips": "Ensure tenon moisture content is 2% lower than seat blank so joints swell tight permanently.",
                    "aesthetic_rhythm": "7-spindle graduated fan back with steam-bent bow top rail"
                },
                {
                    "title": f"Craftsman Mission Slat {item['name']}",
                    "badge": "Arts & Crafts Heritage",
                    "description": f"Architectural rectilinear {item['name']} featuring exposed square through-tenons and pyramid post caps.",
                    "dimensions": "Width: 50 cm | Depth: 50 cm | Height: 98 cm | Seat Height: 46 cm",
                    "recommended_joinery": "Through mortise & tenon with pinned hardwood dowels",
                    "recommended_finish": "Fumed Rich Amber Tone with Low-Sheen Hardwax",
                    "load_capacity": "Robust commercial structural capacity (200 kg)",
                    "blueprint_tips": "Chamfer tenon ends slightly before driving to prevent face tearout on through-mortises.",
                    "aesthetic_rhythm": "Quad-linear vertical back slats with heavy 45x45mm square corner posts"
                }
            ]
        elif "Table" in cat or "Desks" in cat:
            base_patterns = [
                {
                    "title": f"Architectural Trestle Base {item['name']}",
                    "badge": "Refined Rustic",
                    "description": f"Solid timber {item['name']} featuring heavy trestle uprights and a wedged through-tenon stretcher beam.",
                    "dimensions": "Length: 210 cm | Width: 95 cm | Height: 76 cm | Top Slab: 40 mm",
                    "recommended_joinery": "Wedged through-tenon center beam with slotted breadboard ends",
                    "recommended_finish": "Food-Safe Ceramic Matte Hardwax Oil",
                    "load_capacity": "Heavy distributed loads (220–280 kg)",
                    "blueprint_tips": "Slotted outer breadboard screw holes allow lateral seasonal tabletop expansion without splitting.",
                    "aesthetic_rhythm": "Substantial timber uprights with chamfered bridge feet and center stretcher"
                },
                {
                    "title": f"Mid-Century Flared Taper {item['name']}",
                    "badge": "Contemporary Elegance",
                    "description": f"Clean-lined {item['name']} with splayed round tapered legs, beveled undercut edge, and setback aprons.",
                    "dimensions": "Length: 180 cm | Width: 90 cm | Height: 75 cm | Apron: 65 mm",
                    "recommended_joinery": "Mortise & tenon apron frame attached to tabletop via steel expansion Z-clips",
                    "recommended_finish": "Satin 3-Coat Polyurethane System",
                    "load_capacity": "Daily residential dining/work surface (150 kg)",
                    "blueprint_tips": "Fasten tabletop with slotted buttons or Z-clips; never glue or pocket-screw solid tops to aprons.",
                    "aesthetic_rhythm": "60-degree beveled bottom edge producing a visually lightweight floating silhouette"
                },
                {
                    "title": f"Minimalist Waterfall Miter {item['name']}",
                    "badge": "Architectural Modern",
                    "description": f"Continuous wood grain cascades seamlessly from horizontal surface down vertical leg panels.",
                    "dimensions": "Length: 160 cm | Width: 80 cm | Height: 75 cm | Core: 38 mm",
                    "recommended_joinery": "45-degree full miter waterfall joint reinforced with internal blind hardwood splines",
                    "recommended_finish": "Ultra-Matte Moisture Resistant Polyx-Oil",
                    "load_capacity": "Rigid monolithic capacity (180 kg)",
                    "blueprint_tips": "Cut miters on matched sequence boards so grain wraps uninterrupted across the corner.",
                    "aesthetic_rhythm": "Monolithic continuous grain wrap with zero visible apron frames"
                },
                {
                    "title": f"Live-Edge Organic Pedestal {item['name']}",
                    "badge": "Natural Organic Form",
                    "description": f"Bookmatched natural edge timber top stabilized with decorative butterfly keys on sculptural base.",
                    "dimensions": "Length: 190 cm | Width: 85–100 cm | Height: 76 cm | Slab: 45 mm",
                    "recommended_joinery": "Contrasting timber butterfly/bow-tie keys spanning natural fissures; sliding dovetail cleats",
                    "recommended_finish": "Penetrating Hardwax Oil with satin friction buffing",
                    "load_capacity": "Heavy solid slab capacity (250 kg)",
                    "blueprint_tips": "Rout butterfly keys to 2/3 slab thickness with grain perpendicular to fissure.",
                    "aesthetic_rhythm": "Organic natural contour paired with architectural geometry"
                }
            ]
        elif "Storage" in cat or "Shelving" in cat:
            base_patterns = [
                {
                    "title": f"Mid-Century Sliding Tambour {item['name']}",
                    "badge": "Nordic Studio",
                    "description": f"Clean-lined {item['name']} with flexible wood-slat tambour sliding doors and concealed brass runners.",
                    "dimensions": "Width: 160 cm | Depth: 45 cm | Height: 78 cm | Plinth: 18 cm",
                    "recommended_joinery": "Mitred carcass with hidden splines and curved router-cut tambour guide tracks",
                    "recommended_finish": "Warm Amber Danish Oil with Microcrystalline Wax",
                    "load_capacity": "Full interior storage loading (120–160 kg)",
                    "blueprint_tips": "Glue individual wooden tambour slats onto heavy canvas duck backing with flexible PVA.",
                    "aesthetic_rhythm": "Seamless curving door action with integrated vertical pull grooves"
                },
                {
                    "title": f"Architectural Asymmetric Grid {item['name']}",
                    "badge": "Geometric Modernism",
                    "description": f"Multi-tier {item['name']} with varying compartment proportions creating a sculptural storage wall.",
                    "dimensions": "Width: 140 cm | Depth: 35 cm | Height: 190 cm | Cubbies: 7 Bays",
                    "recommended_joinery": "Stopped housing dado joints reinforced with rear structural vertical ribs",
                    "recommended_finish": "Matte Hardwax Polyx-Oil",
                    "load_capacity": "Heavy book collection capacity (220 kg distributed)",
                    "blueprint_tips": "Dado joints should penetrate 1/3 of upright thickness to avoid weakening vertical stiles.",
                    "aesthetic_rhythm": "Balanced asymmetric negative space ideal for combined books and curated objects"
                },
                {
                    "title": f"Floating French-Cleat Wall {item['name']}",
                    "badge": "Cantilevered Minimalist",
                    "description": f"Wall-hung {item['name']} suspended without floor supports, giving modern spaciousness.",
                    "dimensions": "Width: 150 cm | Depth: 38 cm | Height: 45 cm",
                    "recommended_joinery": "Locked miters with continuous grain wrap and internal heavy-duty 45° French cleat",
                    "recommended_finish": "Durable Moisture-Resistant Satin Varnish",
                    "load_capacity": "Wall-anchored distributed load (90 kg)",
                    "blueprint_tips": "Anchor hardwood French cleat directly into wall studs with Grade 8 lag bolts.",
                    "aesthetic_rhythm": "Clean floating shadow line beneath lower carcass"
                },
                {
                    "title": f"Traditional Inset-Panel Heritage {item['name']}",
                    "badge": "Master Millwork",
                    "description": f"Classic {item['name']} with raised panel doors, molded crown detail, and mortised face frames.",
                    "dimensions": "Width: 120 cm | Depth: 55 cm | Height: 185 cm",
                    "recommended_joinery": "Coped rail-and-stile doors with floating solid wood raised panels and mortised frames",
                    "recommended_finish": "Hand-Applied Glaze over Penetrating Oil Topcoat",
                    "load_capacity": "Maximum structural utility capacity (200 kg)",
                    "blueprint_tips": "Never glue door panels into stiles; use rubber space balls to maintain centered floating fit.",
                    "aesthetic_rhythm": "Classic architectural molding profiles and traditional mortised hinges"
                }
            ]
        elif "Bed" in cat or "Bedroom" in cat:
            base_patterns = [
                {
                    "title": f"Cantilevered Floating Platform {item['name']}",
                    "badge": "Modern Architectural",
                    "description": f"Low-profile platform {item['name']} supported on a deeply recessed pedestal base, creating a levitating aesthetic.",
                    "dimensions": "Length: 215 cm | Width: 190 cm | Headboard Height: 95 cm | Recessed Plinth: 20 cm",
                    "recommended_joinery": "Heavy knockdown bed-bolt corner brackets with center I-beam support rail",
                    "recommended_finish": "Natural Matte Hardwax Oil",
                    "load_capacity": "Dual occupant dynamic mattress load (350–450 kg)",
                    "blueprint_tips": "Center beam requires an adjustable central foot touching floor to eliminate mid-span deflection.",
                    "aesthetic_rhythm": "Continuous horizontal grain headboard spanning beyond mattress width"
                },
                {
                    "title": f"Mid-Century Spindle Slat {item['name']}",
                    "badge": "Artisan Craft",
                    "description": f"Turned cylindrical uprights supporting a tapered crest rail and airy vertical spindle headboard.",
                    "dimensions": "Length: 210 cm | Width: 165 cm | Headboard Height: 105 cm",
                    "recommended_joinery": "Turned round tenons fitted into precision drilled angled crest rail holes",
                    "recommended_finish": "Danish Oil with Carnauba Wax Polish",
                    "load_capacity": "Heavy residential capacity (350 kg)",
                    "blueprint_tips": "Bore spindle holes using a dedicated drill guide block to ensure identical compound angles.",
                    "aesthetic_rhythm": "Light airy rhythm allowing wall color and light to pass through"
                },
                {
                    "title": f"Live-Edge Organic Slab {item['name']}",
                    "badge": "Rustic Luxury",
                    "description": f"Statement headboard carved from a single continuous organic timber slab with natural cambium contour.",
                    "dimensions": "Length: 218 cm | Width: 195 cm | Headboard Height: 115 cm | Slab: 45 mm",
                    "recommended_joinery": "Rear vertical steel sliding dovetail stiffeners allowing movement while keeping slab flat",
                    "recommended_finish": "Deep Penetrating Tung Oil with Satin Topcoat",
                    "load_capacity": "Solid heirloom capacity (450 kg)",
                    "blueprint_tips": "Slotted holes in rear vertical mounting irons allow seasonal cross-grain expansion.",
                    "aesthetic_rhythm": "Dramatic organic natural edge contrasting with crisp rectilinear bed rails"
                },
                {
                    "title": f"Post-and-Beam Craftsman {item['name']}",
                    "badge": "Heritage Structural",
                    "description": f"Sturdy mortise-and-tenon structural bed with prominent square corner posts and faceted peg accents.",
                    "dimensions": "Length: 215 cm | Width: 175 cm | Headboard Height: 120 cm | Posts: 85 x 85 mm",
                    "recommended_joinery": "Draw-bored mortise and tenons locked with faceted contrasting hardwood pegs",
                    "recommended_finish": "Fumed Rich Walnut Tone with Matte Polyx-Oil",
                    "load_capacity": "Extreme structural capacity (500 kg)",
                    "blueprint_tips": "Offset peg hole by 2mm toward tenon shoulder so driving the peg pulls the joint immovably tight.",
                    "aesthetic_rhythm": "Substantial timber posts with pyramid finials and horizontal rail banding"
                }
            ]
        else:
            base_patterns = [
                {
                    "title": f"Contemporary Minimalist {item['name']}",
                    "badge": "Architectural Studio",
                    "description": f"Refined solid wood {item['name']} engineered for durability, clean visual geometry, and premium finish.",
                    "dimensions": "Standard Ergonomic Scale | Precision Finished Proportions",
                    "recommended_joinery": "Concealed floating tenons or reinforced locked miters",
                    "recommended_finish": "Protective Matte Hardwax Oil",
                    "load_capacity": "Standard structural demand capacity",
                    "blueprint_tips": "Select straight-grained rift or quarter-sawn stock for primary load-bearing members.",
                    "aesthetic_rhythm": "Refined proportions with subtle 3mm shadow reveal detailing"
                },
                {
                    "title": f"Heritage Fine Joinery {item['name']}",
                    "badge": "Master Craftsman",
                    "description": f"Traditional heirloom {item['name']} celebrating authentic handcrafted joinery and contrasting timber accents.",
                    "dimensions": "Handcrafted Proportion Standard",
                    "recommended_joinery": "Exposed through-tenons or half-lap joints pinned with hardwood dowels",
                    "recommended_finish": "Hand-Rubbed Danish Oil with Beeswax Buffing",
                    "load_capacity": "Heirloom grade structural rating",
                    "blueprint_tips": "Pre-test all joint fits with scrap stock before final assembly and gluing.",
                    "aesthetic_rhythm": "Visible authentic joinery celebrating timber craftsmanship"
                },
                {
                    "title": f"Sculptural Mid-Century {item['name']}",
                    "badge": "Organic Modernism",
                    "description": f"Flowing curved lines and tapered members creating an artistic visual centerpiece.",
                    "dimensions": "Ergonomic Sculpted Scale",
                    "recommended_joinery": "Reinforced mortise & tenon with sculpted transition fillets",
                    "recommended_finish": "Satin Polyurethane 3-Coat System",
                    "load_capacity": "Daily domestic structural capacity",
                    "blueprint_tips": "Shape transitions with rasps and scrapers to achieve seamless tactile curves.",
                    "aesthetic_rhythm": "Organic sculpted fillets with compound beveled edges"
                }
            ]

    # 2. Enrich with selected wood compatibility notes if wood_id is provided
    wood_info = None
    if wood_id:
        wood_info = scoring_engine.WOODS_BY_ID.get(wood_id)
        
    enriched = []
    for pat in base_patterns:
        p_copy = dict(pat)
        if wood_info:
            w_name = wood_info["name"]
            w_mor = wood_info.get("mor", 90.0)
            req_mor = item.get("structuralDemands", {}).get("minMOR", 80)
            margin = round(((w_mor - req_mor) / req_mor) * 100, 1)
            margin_str = f"+{margin}%" if margin >= 0 else f"{margin}%"
            
            p_copy["wood_pairing_name"] = w_name
            p_copy["wood_pairing_note"] = (
                f"Crafting with {w_name} ({w_mor:.1f} MPa MOR): Provides a {margin_str} structural safety margin. "
                f"{wood_info.get('joineryTip', '')}"
            )
            p_copy["wood_stability_note"] = (
                f"Dimensional Stability: Score {wood_info.get('shrinkage', {}).get('stability_score', 7.5)}/10. "
                f"Hardness: {wood_info.get('hardness', 5000)} N (Janka)."
            )
        else:
            p_copy["wood_pairing_name"] = "All Recommended Species"
            p_copy["wood_pairing_note"] = "Fully compatible with all top-ranked species in the recommendation suite."
            p_copy["wood_stability_note"] = "Select quarter-sawn stock for optimal dimensional stability across seasonal cycles."
        enriched.append(p_copy)
        
    return enriched
